use pyo3::{prelude::*, exceptions::PyValueError};
use rayon::prelude::*;
use crate::scorer::*;

/// closest(target, candidates, /, algorithm='levenshtein')
/// --
/// 
/// Find the closest match to the target string in the candidates.
#[pyfunction(algorithm = "\"levenshtein\"")]
pub fn closest(target: &str, options: Vec<&str>, algorithm: &str) -> PyResult<String> {
    if !["LEVENSHTEIN", "JARO", "JAROWINKLER", "HAMMING"].contains(&algorithm.to_uppercase().as_str()) {
        return Err(PyValueError::new_err(format!(
            "Unsupported algorithm: {}",
            algorithm
        )));
    }
    let scorer = match algorithm.to_uppercase().as_str() {
        "JARO" => jaro_similarity,
        "JAROWINKLER" => jaro_winkler_similarity,
        "HAMMING" => hamming_distance,
        "LEVENSHTEIN" => levenshtein_distance,
        _ => unreachable!(),
    };
    if algorithm.to_uppercase().as_str() == "HAMMING" {
        for option in &options {
            if option.len() != target.len() {
                return Err(PyValueError::new_err("Words must be the same length"));
            }
        }
    }
    let mut score = f64::MAX;
    let mut best = "";
    let scores: Vec<(f64, &&str)> = options
        .par_iter()
        .map(|option| (scorer(target, option).unwrap(), option))
        .collect::<Vec<_>>();
    if algorithm.to_uppercase().as_str() == "LEVENSHTEIN"
        || algorithm.to_uppercase().as_str() == "HAMMING"
    {
        for (s, option) in scores {
            if s < score {
                score = s;
                best = option;
            }
        }
    } else {
        score = f64::MIN;
        for (s, option) in scores {
            if s > score {
                score = s;
                best = option;
            }
        }
    }
    return Ok(best.to_owned());
}

/// n_closest(target, candidates, n, /, algorithm='levenshtein')
/// --
/// 
/// Find the n closest matches to the target string in the candidates.
#[pyfunction(algorithm = "\"levenshtein\"")]
pub fn n_closest(
    target: &str,
    options: Vec<&str>,
    n: usize,
    algorithm: &str,
) -> PyResult<Vec<String>> {
    if !["LEVENSHTEIN", "JARO", "JAROWINKLER", "HAMMING"].contains(&algorithm.to_uppercase().as_str()) {
        return Err(PyValueError::new_err(format!(
            "Unsupported algorithm: {}",
            algorithm
        )));
    }
    let scorer = match algorithm.to_uppercase().as_str() {
        "JARO" => jaro_similarity,
        "JAROWINKLER" => jaro_winkler_similarity,
        "HAMMING" => hamming_distance,
        "LEVENSHTEIN" => levenshtein_distance,
        _ => unreachable!(),
    };
    if algorithm.to_uppercase().as_str() == "HAMMING" {
        for option in &options {
            if option.len() != target.len() {
                return Err(PyValueError::new_err("Words must be the same length"));
            }
        }
    }
    let mut scores = options
        .par_iter()
        .map(|option| (option, scorer(target, option).unwrap()))
        .collect::<Vec<_>>();
    if algorithm.to_uppercase().as_str() == "LEVENSHTEIN"
        || algorithm.to_uppercase().as_str() == "HAMMING"
    {
        scores.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
    } else {
        scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
    }
    let mut best: Vec<String> = Vec::new();
    for (option, _) in scores.iter().take(n) {
        best.push(String::from(**option));
    }
    return Ok(best);
}