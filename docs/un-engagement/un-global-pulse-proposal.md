# UN Global Pulse Project Collaboration Proposal

**Organization**: EvoMap (https://github.com/EvoMap)
**Project**: Global Welfare Monitor
**Collaboration type**: Collaborate on a Project
**Submission portal**: https://www.unglobalpulse.org/partner-with-us/

---

## Project Summary

The Global Welfare Monitor is an open-source, automated pipeline that aggregates
publicly available welfare data from five authoritative sources (World Bank, WHO,
GDACS, FAO, UNESCO), applies statistical analysis (composite indexing, anomaly
detection, trend analysis, inequality measurement), and publishes standardized,
machine-readable datasets to the Humanitarian Data Exchange (HDX) platform.

All code is publicly available under an open-source license. The pipeline runs
on a weekly schedule via GitHub Actions, producing SDMX-CSV and HXL-tagged
outputs that conform to UN statistical data exchange standards.

## Problem Statement

Welfare monitoring data exists across multiple siloed systems. Researchers,
policymakers, and humanitarian responders must manually collect, clean, and
reconcile data from disparate APIs, each with different formats, update
frequencies, and access patterns. This fragmentation slows response times
and reduces the quality of cross-domain analysis.

## Proposed Solution

An automated, reproducible, open-source data integration pipeline that:

1. **Aggregates** data from 5 authoritative sources weekly
2. **Analyzes** cross-domain patterns (health-economy correlations,
   food security trends, disaster impact on welfare indicators)
3. **Publishes** standardized datasets to HDX in HXL-tagged CSV format
4. **Generates** composite welfare indices for country-level comparison
5. **Detects** anomalies and emerging crises using statistical methods

## Technical Architecture

```
Data Sources                Pipeline              Outputs
-----------                --------              -------
World Bank API  -->  [Ingestion Layer]  -->  HXL-CSV (HDX)
WHO GHO API     -->  [Analysis Layer]   -->  SDMX-CSV (UN Stats)
GDACS RSS       -->  [Reporting Layer]  -->  PDF Reports
FAO FAOSTAT     -->  [Quality Control]  -->  REST API
UNESCO UIS      -->  [Anomaly Detection] --> Composite Index
```

## Data Sources and Indicators

| Source | Indicators | Update Frequency |
|--------|-----------|-----------------|
| World Bank (wbgapi) | GDP per capita, poverty rate, population, school enrollment, health expenditure | Monthly |
| WHO GHO | Life expectancy, infant mortality, under-5 mortality, maternal mortality, NCD mortality | Monthly |
| GDACS | Earthquakes, floods, cyclones, droughts (real-time alerts) | Weekly |
| FAO FAOSTAT | Consumer food price indices by country | Monthly |
| UNESCO UIS | Enrollment rates, literacy rates, out-of-school children | Quarterly |

## Value Proposition for UN Global Pulse

1. **Open and reproducible**: All code, methods, and data are publicly auditable
2. **Standards-compliant**: SDMX-CSV and HXL output formats
3. **Automated**: No manual intervention required for weekly data updates
4. **Cross-domain**: Integrates health, economic, food security, education,
   and disaster data for holistic welfare assessment
5. **Scalable**: Adding new data sources requires only implementing
   a new ingestion module following the established pattern

## Alignment with UN Global Pulse Priorities

- **Data innovation for sustainable development**: Automated integration
  of SDG-relevant indicators
- **Real-time crisis monitoring**: GDACS integration for disaster response
- **Open data advocacy**: All outputs published to HDX under CC-BY license
- **Capacity building**: Open-source tools that any organization can deploy

## Team and Organization

EvoMap is an open-source technology organization focused on building
tools for global welfare monitoring and evolutionary computation.
The Global Welfare Monitor project is maintained by contributors
on GitHub at https://github.com/EvoMap/global-welfare-monitor.

## Requested Support

- Technical review and feedback on data quality standards
- Access to UN Global Pulse Pulse Lab resources for validation
- Guidance on additional data sources relevant to crisis monitoring
- Co-publication opportunity for validated datasets

## Timeline

| Phase | Duration | Deliverable |
|-------|---------|------------|
| Data validation | Month 1-2 | Verified data quality against official UN sources |
| HDX publishing | Month 2-3 | Live datasets on HDX platform |
| Composite index | Month 3-4 | Published Global Welfare Composite Index |
| Report automation | Month 4-6 | Automated weekly welfare reports |

## Contact

- GitHub: https://github.com/EvoMap
- Repository: https://github.com/EvoMap/global-welfare-monitor
