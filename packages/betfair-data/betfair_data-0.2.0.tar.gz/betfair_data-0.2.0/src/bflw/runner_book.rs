use core::fmt;
use pyo3::prelude::*;
use pyo3::types::PyList;
use serde::de::{DeserializeSeed, Error, IgnoredAny, MapAccess, Visitor};
use serde::{Deserialize, Deserializer};
use serde_json::value::RawValue;

use super::datetime::DateTimeString;
use super::market_definition_runner::MarketDefRunnerUpdate;
use super::runner_book_ex::{RunnerBookEX, RunnerBookEXUpdate};
use super::runner_book_sp::{RunnerBookSP, RunnerBookSPUpdate};
use crate::bflw::float_str::FloatStr;
use crate::bflw::RoundToCents;
use crate::enums::SelectionStatus;
use crate::ids::SelectionID;
use crate::immutable::container::{PyRep, SyncObj};
use crate::immutable::price_size::{ImmutablePriceSizeBackLadder, ImmutablePriceSizeLayLadder};
use crate::market_source::SourceConfig;
use crate::price_size::{F64OrStr, PriceSize};

#[pyclass]
pub struct RunnerBook {
    #[pyo3(get)]
    pub selection_id: SelectionID,
    #[pyo3(get)]
    pub status: SelectionStatus,
    #[pyo3(get)]
    pub total_matched: f64,
    #[pyo3(get)]
    pub adjustment_factor: Option<f64>,
    #[pyo3(get)]
    pub handicap: FloatStr, // I like this better as Option<f64> buut compat
    #[pyo3(get)]
    pub last_price_traded: Option<FloatStr>,
    #[pyo3(get)]
    pub removal_date: Option<SyncObj<DateTimeString>>,
    #[pyo3(get)]
    pub ex: Py<RunnerBookEX>,
    #[pyo3(get)]
    pub sp: Py<RunnerBookSP>,
    #[pyo3(get)]
    pub matches: Vec<()>,
    #[pyo3(get)]
    pub orders: Vec<()>,
}

pub struct RunnerChangeUpdate {
    handicap: Option<FloatStr>,
    last_price_traded: Option<FloatStr>,
    total_matched: Option<f64>,
    ex: Option<Py<RunnerBookEX>>,
    sp: Option<Py<RunnerBookSP>>,
}

impl PyRep for Vec<Py<RunnerBook>> {
    fn py_rep(&self, py: Python) -> PyObject {
        PyList::new(py, self.iter().map(|ps| ps.into_py(py))).into_py(py)
    }
}

impl RunnerBook {
    pub fn new(id: SelectionID, py: Python) -> Self {
        Self {
            selection_id: id,
            status: Default::default(),
            total_matched: Default::default(),
            adjustment_factor: Default::default(),
            handicap: Default::default(),
            last_price_traded: Default::default(),
            removal_date: Default::default(),
            ex: Py::new(py, RunnerBookEX::default()).unwrap(),
            sp: Py::new(py, RunnerBookSP::default()).unwrap(),
            matches: Default::default(),
            orders: Default::default(),
        }
    }

    pub fn update_from_change(&self, change: RunnerChangeUpdate, py: Python) -> Self {
        Self {
            selection_id: self.selection_id,
            adjustment_factor: self.adjustment_factor,
            status: self.status,
            removal_date: self.removal_date.clone(),
            handicap: change.handicap.unwrap_or(self.handicap),
            last_price_traded: change.last_price_traded.or(self.last_price_traded),
            total_matched: change.total_matched.unwrap_or(self.total_matched),
            ex: change.ex.unwrap_or_else(|| self.ex.clone_ref(py)),
            sp: change.sp.unwrap_or_else(|| self.sp.clone_ref(py)),

            matches: self.matches.clone(), // always empty
            orders: self.orders.clone(),   // always empty
        }
    }

    pub fn would_change(&self, change: &MarketDefRunnerUpdate, py: Python) -> bool {
        self.status != change.status
            || self.adjustment_factor != change.adjustment_factor
            || !change.hc.is_some_with(|h| *h == self.handicap)
            || (change.bsp.is_some() && self.sp.borrow(py).actual_sp != change.bsp)
            || ((self.removal_date.is_none() && change.removal_date.is_some())
                || self
                    .removal_date
                    .is_some_with(|s| !change.removal_date.contains(&s.value.as_str())))
    }

    pub fn update_from_def(&self, change: &MarketDefRunnerUpdate, py: Python) -> Self {
        // need to update sp obj with bsp value
        let sp = if change.bsp.is_some() {
            let sp = self.sp.borrow(py);
            if sp.actual_sp != change.bsp {
                let upt = RunnerBookSPUpdate {
                    actual_sp: change.bsp,
                    ..Default::default()
                };
                sp.update(upt, py)
            } else {
                self.sp.clone_ref(py)
            }
        } else {
            self.sp.clone_ref(py)
        };

        Self {
            selection_id: self.selection_id,
            status: change.status,
            adjustment_factor: change.adjustment_factor.or(self.adjustment_factor),
            handicap: change.hc.unwrap_or(self.handicap),
            last_price_traded: self.last_price_traded,
            total_matched: self.total_matched,
            ex: self.ex.clone_ref(py),
            sp,
            removal_date: change
                .removal_date
                .and_then(|s| match &self.removal_date {
                    Some(rd) if rd.value.as_str() != s => {
                        let dts = DateTimeString::new(s).unwrap(); // TODO: fix unwrap, maybe runner def update should take the dt already passed
                        Some(SyncObj::new(dts))
                    }
                    None => {
                        let dts = DateTimeString::new(s).unwrap();
                        Some(SyncObj::new(dts))
                    }
                    _ => self.removal_date.clone(),
                })
                .or_else(|| self.removal_date.clone()),

            matches: self.matches.clone(), // always empty
            orders: self.orders.clone(),   // always empty
        }
    }
}

pub struct RunnerChangeSeq<'a, 'py>(
    pub Option<&'a Vec<Py<RunnerBook>>>,
    pub Python<'py>,
    pub SourceConfig,
);
impl<'de, 'a, 'py> DeserializeSeed<'de> for RunnerChangeSeq<'a, 'py> {
    type Value = Vec<Py<RunnerBook>>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct RunnerSeqVisitor<'a, 'py>(
            Option<&'a Vec<Py<RunnerBook>>>,
            Python<'py>,
            SourceConfig,
        );
        impl<'de, 'a, 'py> Visitor<'de> for RunnerSeqVisitor<'a, 'py> {
            type Value = Vec<Py<RunnerBook>>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("")
            }

            fn visit_seq<A>(self, mut seq: A) -> Result<Self::Value, A::Error>
            where
                A: serde::de::SeqAccess<'de>,
            {
                // TODO - maybe move to lazy cloning this vec if we detect that the output would actually change
                let mut v = self
                    .0
                    .map(|v| v.iter().map(|r| r.clone_ref(self.1)).collect::<Vec<_>>())
                    .unwrap_or_else(|| Vec::with_capacity(10));

                #[derive(Deserialize)]
                struct RunnerWithID {
                    id: SelectionID,
                }

                while let Some(raw) = seq.next_element::<&RawValue>()? {
                    let mut deser = serde_json::Deserializer::from_str(raw.get());
                    let rid: RunnerWithID =
                        serde_json::from_str(raw.get()).map_err(Error::custom)?;

                    let index = v
                        .iter()
                        .map(|r| r.borrow(self.1))
                        .position(|r| r.selection_id == rid.id);

                    match index {
                        Some(index) => {
                            let runner = {
                                let runner = unsafe { v.get_unchecked(index).borrow(self.1) };
                                RunnerBookChangeDeser(&runner, self.1, self.2)
                                    .deserialize(&mut deser)
                                    .map_err(Error::custom)?
                            };

                            v[index] = Py::new(self.1, runner).unwrap();
                        }
                        None => {
                            let runner = RunnerBook::new(rid.id, self.1);
                            let runner = RunnerBookChangeDeser(&runner, self.1, self.2)
                                .deserialize(&mut deser)
                                .map_err(Error::custom)?;

                            v.push(Py::new(self.1, runner).unwrap());
                        }
                    }
                }

                Ok(v)
            }
        }

        deserializer.deserialize_seq(RunnerSeqVisitor(self.0, self.1, self.2))
    }
}

struct RunnerBookChangeDeser<'a, 'py>(&'a RunnerBook, Python<'py>, SourceConfig);
impl<'de, 'a, 'py> DeserializeSeed<'de> for RunnerBookChangeDeser<'a, 'py> {
    type Value = RunnerBook;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Debug, Deserialize)]
        #[serde(field_identifier, rename_all = "camelCase")]
        enum Field {
            Id,
            Atb,
            Atl,
            Spn,
            Spf,
            Spb,
            Spl,
            Trd,
            Tv,
            Ltp,
            Hc,
        }

        struct RunnerChangeVisitor<'a, 'py>(&'a RunnerBook, Python<'py>, SourceConfig);
        impl<'de, 'a, 'py> Visitor<'de> for RunnerChangeVisitor<'a, 'py> {
            type Value = RunnerBook;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("")
            }

            fn visit_map<V>(self, mut map: V) -> Result<Self::Value, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut atb: Option<Vec<PriceSize>> = None;
                let mut atl: Option<Vec<PriceSize>> = None;
                let mut trd: Option<Vec<PriceSize>> = None;

                let mut spb: Option<Vec<PriceSize>> = None;
                let mut spl: Option<Vec<PriceSize>> = None;
                let mut spn: Option<FloatStr> = None;
                let mut spf: Option<FloatStr> = None;

                let mut tv: Option<f64> = None;
                let mut ltp: Option<FloatStr> = None;
                let mut hc: Option<FloatStr> = None;

                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Id => {
                            let id = map.next_value::<SelectionID>()?;
                            debug_assert!(id == self.0.selection_id);
                        }
                        Field::Atb => {
                            let ex = self.0.ex.borrow(self.1);

                            if self.0.selection_id == 21534802 {
    
                                let raw = map.next_value::<&RawValue>()?;
                                // println!("{}", raw.get());
    
                                let mut deser = serde_json::Deserializer::from_str(raw.get());
                                atb = Some(ImmutablePriceSizeLayLadder(&ex.available_to_back.value).deserialize(&mut deser).unwrap());

                            } else {
                                atb = Some(map.next_value_seed(ImmutablePriceSizeLayLadder(
                                    &ex.available_to_back.value,
                                ))?);
                            }
                        }
                        Field::Atl => {
                            let ex = self.0.ex.borrow(self.1);
                            atl = Some(map.next_value_seed(ImmutablePriceSizeBackLadder(
                                &ex.available_to_lay.value,
                            ))?);
                        }
                        Field::Trd => {
                            let ex = self.0.ex.borrow(self.1);
                            let l = map.next_value_seed(ImmutablePriceSizeBackLadder(
                                &ex.traded_volume.value,
                            ))?;

                            if self.2.cumulative_runner_tv {
                                tv = Some(l.iter().map(|ps| ps.size).sum::<f64>().round_cent());
                            }

                            trd = Some(l);
                        }
                        Field::Spb => {
                            let sp = self.0.sp.borrow(self.1);
                            spl = Some(map.next_value_seed(ImmutablePriceSizeLayLadder(
                                &sp.lay_liability_taken.value,
                            ))?);
                        }
                        Field::Spl => {
                            let sp = self.0.sp.borrow(self.1);
                            spb = Some(map.next_value_seed(ImmutablePriceSizeBackLadder(
                                &sp.back_stake_taken.value,
                            ))?);
                        }
                        Field::Spn => {
                            spn = Some(map.next_value::<FloatStr>()?);
                        }
                        Field::Spf => {
                            spf = Some(map.next_value::<FloatStr>()?);
                        }
                        Field::Ltp => {
                            ltp = Some(map.next_value::<FloatStr>()?);
                        }
                        Field::Hc => {
                            hc = Some(map.next_value::<FloatStr>()?);
                        }
                        // The betfair historic data files differ from the stream here, they send tv deltas
                        // that need to be accumulated, whereas the stream sends the value itself.
                        Field::Tv => {
                            if self.2.cumulative_runner_tv {
                                map.next_value::<IgnoredAny>()?;
                            } else {
                                let v: f64 = map.next_value::<F64OrStr>()?.into();
                                let v = v.round_cent();
                                tv = Some(v);
                            }
                        }
                    };
                }

                let ex = if atb.is_some() || atl.is_some() || trd.is_some() {
                    let upt = RunnerBookEXUpdate {
                        available_to_back: atb,
                        available_to_lay: atl,
                        traded_volume: trd,
                    };

                    Some(self.0.ex.borrow(self.1).update(upt, self.1))
                } else {
                    None
                };

                let sp = if spl.is_some() || spb.is_some() || spn.is_some() || spf.is_some() {
                    let upt = RunnerBookSPUpdate {
                        actual_sp: None,
                        far_price: spf,
                        near_price: spn,
                        back_stake_taken: spb,
                        lay_liability_taken: spl,
                    };

                    Some(self.0.sp.borrow(self.1).update(upt, self.1))
                } else {
                    None
                };

                let update = RunnerChangeUpdate {
                    handicap: hc,
                    last_price_traded: ltp,
                    total_matched: tv,
                    ex,
                    sp,
                };

                Ok(self.0.update_from_change(update, self.1))
            }
        }

        const FIELDS: &[&str] = &[
            "id", "atb", "atl", "spn", "spf", "spb", "spl", "trd", "tv", "ltp", "hc",
        ];
        deserializer.deserialize_struct(
            "RunnerChange",
            FIELDS,
            RunnerChangeVisitor(self.0, self.1, self.2),
        )
    }
}
