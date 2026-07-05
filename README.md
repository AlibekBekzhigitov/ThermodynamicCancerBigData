# Thermodynamic Cancer Big Data

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Apache Spark](https://img.shields.io/badge/Apache-Spark-orange.svg)](https://spark.apache.org/)

This project investigates oncological progression through the lens of non-equilibrium thermodynamics and information theory. We model cancer cell lines as dissipative structures, utilizing genomic copy number variation (CNV) and viability screening data to quantify genomic entropy ($S$) and identify critical phase transitions (bifurcation points).

##  Scientific Context
By applying the Boltzmann-Shannon entropy formula to genomic data, we demonstrate that high genomic entropy correlates with a loss of cellular homeostatic capacity. Our model identifies specific entropy thresholds where cancer cells undergo a phase transition, offering a potential framework for future therapeutic targeting.

## System Architecture
The project employs a robust Big Data pipeline:
* **Ingestion:** Real-time data streaming via **Apache Kafka** (`producer.py`).
* **Analytics:** Distributed processing with **Apache Spark** to handle 19,000+ gene features per cell line.
* **Modeling:** Non-linear analysis using **Spark MLlib (GBTRegressor)** to map the entropy-viability relationship.

## Getting Started

### Prerequisites
* Python 3.13+
* Java (JDK) 17+ (Required for Apache Spark)
