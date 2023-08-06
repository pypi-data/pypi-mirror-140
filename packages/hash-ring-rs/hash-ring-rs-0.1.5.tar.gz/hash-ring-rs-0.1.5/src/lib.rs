use std::collections::HashSet;

use pyo3::prelude::*;
use sha2::{Digest, Sha256};

#[pyclass]
struct HashRing {
    vnodes: u32,
    ring: Vec<(u32, String)>,
}

#[pymethods]
impl HashRing {
    #[new]
    pub fn new(vnodes: i32) -> Self {
        HashRing {
            vnodes: vnodes as u32,
            ring: Vec::new(),
        }
    }

    pub fn add_node(&mut self, name: &str) {
        for idx in 0..self.vnodes {
            self.ring.push((Self::ring_node_hash(name, idx), name.to_string()));
        }
    }

    pub fn remove_node(&mut self, name: &str) {
        self.ring.retain(|(_, node_name)| node_name != name);
    }

    pub fn sort(&mut self) {
        self.ring.sort();
    }

    #[getter]
    pub fn nodes(&self) -> HashSet<String> {
        self.ring.iter()
            .map(|(_, node)| node.clone())
            .collect()
    }

    pub fn get_node(&self, value: &str) -> String {
        if self.ring.is_empty() {
            return "".into();
        }

        let value_hash = Self::ring_hash(value);
        let (mut left, mut right, mut middle) = (0, self.ring.len() - 1, self.ring.len() / 2);
        while right - left > 1 {
            let (hash, _) = &self.ring[middle];
            if hash > &value_hash {
                right = middle;
            } else {
                left = middle;
            }
            middle = (left + right) / 2;
        }
        self.ring[right].1.clone()
    }

    pub fn get_items_for_node(&self, max: u32, node: &str) -> Vec<u32> {
        if self.ring.is_empty() {
            return Vec::new();
        }

        let mut selection = vec![];
        for i in 0..max {
            if self.get_node(&i.to_string()) == node {
                selection.push(i);
            }
        }
        selection
    }
}

impl HashRing {
    fn ring_node_hash(node_name: &str, idx: u32) -> u32 {
        Self::ring_hash(&format!("{}_{}", node_name, idx))
    }

    fn ring_hash(value: &str) -> u32 {
        let digest = Sha256::digest(value.as_bytes());
        let mut slice = [0; 4];
        slice.copy_from_slice(&digest[..4]);
        u32::from_be_bytes(slice)
    }
}

#[pymodule]
fn hash_ring_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<HashRing>()?;
    Ok(())
}
