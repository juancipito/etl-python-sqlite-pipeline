-- Average CSAT and resolution rate by region and channel.
SELECT
  region,
  channel,
  ROUND(AVG(csat_score), 2) AS avg_csat,
  ROUND(SUM(resolved_contacts) * 1.0 / SUM(contacts), 3) AS resolution_rate
FROM operations_clean
GROUP BY region, channel
ORDER BY region, channel;

-- Daily contact volume.
SELECT date, SUM(contacts) AS total_contacts
FROM operations_clean
GROUP BY date
ORDER BY date;
