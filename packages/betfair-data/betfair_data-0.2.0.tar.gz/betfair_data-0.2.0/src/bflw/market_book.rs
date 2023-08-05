use pyo3::prelude::*;
use serde::de::{DeserializeSeed, Error, IgnoredAny, MapAccess, Visitor};
use serde::{Deserialize, Deserializer};
use serde_json::value::RawValue;
use std::fmt;

use super::datetime::{DateTime, DateTimeString};
use super::market_definition::MarketDefinition;
use super::runner_book::RunnerBook;
use crate::bflw::market_definition::MarketDefinitionDeser;
use crate::bflw::runner_book::RunnerChangeSeq;
use crate::bflw::RoundToCents;
use crate::enums::MarketStatus;
use crate::ids::MarketID;
use crate::immutable::container::SyncObj;
use crate::market_source::SourceConfig;

/*
class MarketBook(BaseResource):


def __init__(self, **kwargs):
    self.streaming_unique_id = kwargs.pop("streaming_unique_id", None)
    self.streaming_update = kwargs.pop("streaming_update", None)
    self.streaming_snap = kwargs.pop("streaming_snap", False)
    self.market_definition = kwargs.pop("market_definition", None)
    super(MarketBook, self).__init__(**kwargs)
    self.market_id = kwargs.get("marketId")
    self.bet_delay = kwargs.get("betDelay")
    self.bsp_reconciled = kwargs.get("bspReconciled")
    self.complete = kwargs.get("complete")
    self.cross_matching = kwargs.get("crossMatching")
    self.inplay = kwargs.get("inplay")
    self.is_market_data_delayed = kwargs.get("isMarketDataDelayed")
    self.last_match_time = self.strip_datetime(kwargs.get("lastMatchTime"))
    self.number_of_active_runners = kwargs.get("numberOfActiveRunners")
    self.number_of_runners = kwargs.get("numberOfRunners")
    self.number_of_winners = kwargs.get("numberOfWinners")
    self.runners_voidable = kwargs.get("runnersVoidable")
    self.status = kwargs.get("status")
    self.total_available = kwargs.get("totalAvailable")
    self.total_matched = kwargs.get("totalMatched")
    self.version = kwargs.get("version")
    self.runners = [RunnerBook(**i) for i in kwargs.get("runners")]
    self.publish_time = self.strip_datetime(kwargs.get("publishTime"))
    self.publish_time_epoch = kwargs.get("publishTime")
    self.key_line_description = (
        KeyLine(**kwargs.get("keyLineDescription"))
        if kwargs.get("keyLineDescription")
        else None
    )
    self.price_ladder_definition = (
        PriceLadderDescription(**kwargs.get("priceLadderDefinition"))
        if kwargs.get("priceLadderDefinition")
        else None
    )

"""
:type bet_delay: int
:type bsp_reconciled: bool
:type complete: bool
:type cross_matching: bool
:type inplay: bool
:type is_market_data_delayed: bool
:type last_match_time: datetime.datetime
:type market_id: unicode
:type number_of_active_runners: int
:type number_of_runners: int
:type number_of_winners: int
:type publish_time: datetime.datetime
:type runners: list[RunnerBook]
:type runners_voidable: bool
:type status: unicode
:type total_available: float
:type total_matched: float
:type version: int
"""

+ market_definition
*/

// store the current state of the market mutably
#[pyclass]
pub struct MarketBook {
    #[pyo3(get)]
    pub publish_time: DateTime,
    #[pyo3(get)]
    pub bet_delay: u16,
    #[pyo3(get)]
    pub bsp_reconciled: bool,
    #[pyo3(get)]
    pub complete: bool,
    #[pyo3(get)]
    pub cross_matching: bool,
    #[pyo3(get)]
    pub inplay: bool,
    #[pyo3(get)]
    pub is_market_data_delayed: Option<bool>,
    #[pyo3(get)]
    pub number_of_active_runners: u16,
    #[pyo3(get)]
    pub number_of_runners: u16,
    #[pyo3(get)]
    pub number_of_winners: u8,
    #[pyo3(get)]
    pub runners_voidable: bool,
    #[pyo3(get)]
    pub status: MarketStatus,
    #[pyo3(get)]
    pub total_available: Option<()>, // f64 but bflw doesnt seem to use this on historic files
    #[pyo3(get)]
    pub total_matched: f64,
    #[pyo3(get)]
    pub version: u64,
    #[pyo3(get)]
    pub runners: SyncObj<Vec<Py<RunnerBook>>>,
    #[pyo3(get)]
    pub market_definition: Py<MarketDefinition>,
    #[pyo3(get)]
    pub market_id: SyncObj<MarketID>,
    #[pyo3(get)]
    pub last_match_time: Option<SyncObj<DateTimeString>>,
}

#[derive(Default)]
struct MarketBookUpdate<'a> {
    market_id: &'a str,
    definition: Option<MarketDefinition>,
    runners: Option<Vec<Py<RunnerBook>>>,
    total_volume: Option<f64>,
}

#[pymethods]
impl MarketBook {
    #[getter(publish_time_epoch)]
    fn get_publish_time_epoch(&self, py: Python) -> PyObject {
        let ts = *self.publish_time;
        ts.into_py(py)
    }
}

impl MarketBook {
    fn new(change: MarketBookUpdate, py: Python) -> Self {
        let def = change.definition.unwrap(); // fix unwrap

        // maybe theres a better way to calculate this
        // let available = change
        //     .runners
        //     .as_ref()
        //     .map(|rs| {
        //         rs.iter()
        //             .map(|r| {
        //                 let r = r.borrow(py);
        //                 let ex = r.ex.borrow(py);
        //                 let back: f64 = ex.available_to_back.value.iter().map(|ps| ps.size).sum();
        //                 let lay: f64 = ex.available_to_lay.value.iter().map(|ps| ps.size).sum();
        //                 back + lay
        //             })
        //             .sum::<f64>()
        //     })
        //     .unwrap_or_default();

        Self {
            market_id: SyncObj::new(MarketID::from(change.market_id)),
            runners: SyncObj::new(change.runners.unwrap_or_default()),
            total_matched: change.total_volume.unwrap_or_default(),
            bet_delay: def.bet_delay,
            bsp_reconciled: def.bsp_reconciled,
            complete: def.complete,
            cross_matching: def.cross_matching,
            inplay: def.in_play,
            is_market_data_delayed: None,
            number_of_active_runners: def.number_of_active_runners,
            number_of_runners: def.runners.value.len() as u16,
            runners_voidable: def.runners_voidable,
            status: def.status,
            number_of_winners: def.number_of_winners,
            version: def.version,
            total_available: None, // available,
            market_definition: Py::new(py, def).unwrap(),

            publish_time: DateTime::new(0),
            last_match_time: None,
        }
    }

    fn update_from_change(&self, change: MarketBookUpdate, py: Python) -> Self {
        // let available = change.runners.as_ref().map(|rs| {
        //     rs.iter()
        //         .map(|r| {
        //             let r = r.borrow(py);
        //             let ex = r.ex.borrow(py);
        //             let back: f64 = ex.available_to_back.value.iter().map(|ps| ps.size).sum();
        //             let lay: f64 = ex.available_to_lay.value.iter().map(|ps| ps.size).sum();
        //             back + lay
        //         })
        //         .sum::<f64>()
        // });

        Self {
            market_id: self.market_id.clone(),
            runners: change
                .runners
                .map(SyncObj::new)
                .unwrap_or_else(|| self.runners.clone()),
            total_matched: change.total_volume.unwrap_or(self.total_matched),
            bet_delay: change
                .definition
                .as_ref()
                .map(|def| def.bet_delay)
                .unwrap_or(self.bet_delay),
            bsp_reconciled: change
                .definition
                .as_ref()
                .map(|def| def.bsp_reconciled)
                .unwrap_or(self.bsp_reconciled),
            complete: change
                .definition
                .as_ref()
                .map(|def| def.complete)
                .unwrap_or(self.complete),
            cross_matching: change
                .definition
                .as_ref()
                .map(|def| def.cross_matching)
                .unwrap_or(self.cross_matching),
            inplay: change
                .definition
                .as_ref()
                .map(|def| def.in_play)
                .unwrap_or(self.inplay),
            is_market_data_delayed: None,
            number_of_active_runners: change
                .definition
                .as_ref()
                .map(|def| def.number_of_active_runners)
                .unwrap_or(self.number_of_active_runners),
            number_of_runners: change
                .definition
                .as_ref()
                .map(|def| def.runners.value.len() as u16)
                .unwrap_or(self.number_of_runners),
            runners_voidable: change
                .definition
                .as_ref()
                .map(|def| def.runners_voidable)
                .unwrap_or(self.runners_voidable),
            status: change
                .definition
                .as_ref()
                .map(|def| def.status)
                .unwrap_or(self.status),
            number_of_winners: change
                .definition
                .as_ref()
                .map(|def| def.number_of_winners)
                .unwrap_or(self.number_of_winners),
            version: change
                .definition
                .as_ref()
                .map(|def| def.version)
                .unwrap_or(self.version),
            total_available: None, // available.unwrap_or(self.total_available),
            market_definition: change
                .definition
                .map(|def| Py::new(py, def).unwrap())
                .unwrap_or_else(|| self.market_definition.clone()),

            publish_time: self.publish_time,
            last_match_time: None,
        }
    }
}

pub struct MarketBooksDeser<'a, 'py>(pub &'a [Py<MarketBook>], pub Python<'py>, pub SourceConfig);
impl<'de, 'a, 'py> DeserializeSeed<'de> for MarketBooksDeser<'a, 'py> {
    type Value = Vec<Py<MarketBook>>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Debug, Deserialize)]
        #[serde(field_identifier, rename_all = "lowercase")]
        enum Field {
            Op,
            Clk,
            Pt,
            Mc,
        }

        struct MarketBooksDeserVisitor<'a, 'py>(&'a [Py<MarketBook>], Python<'py>, SourceConfig);
        impl<'de, 'a, 'py> Visitor<'de> for MarketBooksDeserVisitor<'a, 'py> {
            type Value = Vec<Py<MarketBook>>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("")
            }

            fn visit_map<V>(self, mut map: V) -> Result<Self::Value, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut pt: Option<DateTime> = None;
                let mut books: Vec<Py<MarketBook>> = Vec::new();

                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Op => {
                            map.next_value::<IgnoredAny>()?;
                        }
                        Field::Pt => {
                            pt = Some(DateTime::new(map.next_value::<u64>()?));
                        }
                        Field::Clk => {
                            map.next_value::<IgnoredAny>()?;
                        }
                        Field::Mc => {
                            books = map.next_value_seed(MarketMcSeq(self.0, self.1, self.2))?;
                        }
                    }
                }

                if let Some(pt) = pt {
                    books
                        .iter_mut()
                        .for_each(|mb| mb.borrow_mut(self.1).publish_time = pt);
                }

                Ok(books)
            }
        }

        const FIELDS: &[&str] = &["op", "pt", "clk", "mc"];
        deserializer.deserialize_struct(
            "MarketBook",
            FIELDS,
            MarketBooksDeserVisitor(self.0, self.1, self.2),
        )
    }
}

// Used for serializing in place over the marketChange `mc` array
struct MarketMcSeq<'a, 'py>(&'a [Py<MarketBook>], Python<'py>, SourceConfig);
impl<'de, 'a, 'py> DeserializeSeed<'de> for MarketMcSeq<'a, 'py> {
    type Value = Vec<Py<MarketBook>>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct MarketMcSeqVisitor<'a, 'py>(&'a [Py<MarketBook>], Python<'py>, SourceConfig);
        impl<'de, 'a, 'py> Visitor<'de> for MarketMcSeqVisitor<'a, 'py> {
            type Value = Vec<Py<MarketBook>>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("")
            }

            fn visit_seq<A>(self, mut seq: A) -> Result<Self::Value, A::Error>
            where
                A: serde::de::SeqAccess<'de>,
            {
                #[derive(Deserialize)]
                struct MarketWithID<'a> {
                    id: &'a str,
                    img: Option<bool>,
                }

                let mut next_books: Vec<Py<MarketBook>> = Vec::new();

                while let Some(raw) = seq.next_element::<&RawValue>()? {
                    let mut deser = serde_json::Deserializer::from_str(raw.get());
                    let mid: MarketWithID =
                        serde_json::from_str(raw.get()).map_err(Error::custom)?;

                    let mb = {
                        if mid.img.contains(&true) {
                            None
                        } else {
                            next_books
                                .iter()
                                .find(|m| (*m).borrow(self.1).market_id.value.as_str() == mid.id)
                                .or_else(|| {
                                    self.0.iter().find(|m| {
                                        (*m).borrow(self.1).market_id.value.as_str() == mid.id
                                    })
                                })
                                .map(|o| o.borrow(self.1))
                        }
                    };

                    let next_mb = MarketMc(mb, self.1, self.2)
                        .deserialize(&mut deser)
                        .map_err(Error::custom)?;

                    next_books.push(Py::new(self.1, next_mb).unwrap());
                }

                Ok(next_books)
            }
        }

        deserializer.deserialize_seq(MarketMcSeqVisitor(self.0, self.1, self.2))
    }
}

struct MarketMc<'py>(Option<PyRef<'py, MarketBook>>, Python<'py>, SourceConfig);
impl<'de, 'py> DeserializeSeed<'de> for MarketMc<'py> {
    type Value = MarketBook;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Debug, Deserialize)]
        #[serde(field_identifier, rename_all = "camelCase")]
        enum Field {
            Id,
            MarketDefinition,
            Rc,
            Con,
            Img,
            Tv,

            // bflw recorded field
            #[serde(rename = "_stream_id")]
            StreamId,
        }

        struct MarketMcVisitor<'py>(Option<PyRef<'py, MarketBook>>, Python<'py>, SourceConfig);
        impl<'de, 'py> Visitor<'de> for MarketMcVisitor<'py> {
            type Value = MarketBook;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("")
            }

            fn visit_map<V>(self, mut map: V) -> Result<Self::Value, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut upt = MarketBookUpdate::default();
                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Id => {
                            let s = map.next_value::<&str>()?;
                            upt.market_id = s;
                        }
                        Field::MarketDefinition => {
                            let def = self
                                .0
                                .as_ref()
                                .map(|mb| mb.market_definition.borrow(self.1));
                            let runners = upt
                                .runners
                                .as_ref()
                                .or_else(|| self.0.as_ref().map(|mb| mb.runners.value.as_ref()));

                            let (d, r) = map.next_value_seed(MarketDefinitionDeser(
                                def, runners, self.1, self.2,
                            ))?;

                            upt.definition = d;
                            upt.runners = r;
                        }
                        Field::Rc => {
                            let runners = upt
                                .runners
                                .as_ref()
                                .or_else(|| self.0.as_ref().map(|mb| mb.runners.value.as_ref()));
                            upt.runners = Some(
                                map.next_value_seed(RunnerChangeSeq(runners, self.1, self.2))?,
                            );

                            // if cumulative_runner_tv is on, then tv shouldnt be sent at a market level and will have
                            // to be derived from the sum of runner tv's. This happens when using the data provided
                            // from betfair historical data service, not saved from the actual stream
                            if self.2.cumulative_runner_tv {
                                upt.total_volume = upt
                                    .runners
                                    .as_ref()
                                    .map(|rs| {
                                        rs.iter().map(|r| r.borrow(self.1).total_matched).sum()
                                    })
                                    .map(|f: f64| f.round_cent());
                            }
                        }
                        Field::Tv => {
                            if !self.2.cumulative_runner_tv {
                                upt.total_volume = Some(map.next_value::<f64>()?.round_cent());
                            } else {
                                map.next_value::<IgnoredAny>()?;
                            }
                        }
                        Field::Con => {
                            map.next_value::<IgnoredAny>()?;
                        }
                        Field::Img => {
                            map.next_value::<IgnoredAny>()?;
                        }
                        _ => {
                            map.next_value::<IgnoredAny>()?;
                        }
                    }
                }

                let mb = match (self.0, &upt.definition) {
                    (Some(mb), Some(_)) => mb.update_from_change(upt, self.1),
                    (Some(mb), None) => mb.update_from_change(upt, self.1),
                    (None, Some(_)) => MarketBook::new(upt, self.1),
                    (None, None) => {
                        return Err(Error::custom("missing definition on initial market update"))
                    }
                };

                Ok(mb)
            }
        }

        const FIELDS: &[&str] = &["id", "marketDefinition", "rc", "con", "img", "tv"];
        deserializer.deserialize_struct(
            "MarketChange",
            FIELDS,
            MarketMcVisitor(self.0, self.1, self.2),
        )
    }
}
