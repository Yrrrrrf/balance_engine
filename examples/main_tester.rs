#![allow(unused)]

use dev_utils::{app_dt, dlog::set_max_level};
use std::{thread, time::Duration};

fn main() {
    // app_dt!(file!());
    app_dt!(file!(), "package" => ["license", "keywords", "description", "authors"]);
    set_max_level(dev_utils::dlog::Level::Trace);

}
