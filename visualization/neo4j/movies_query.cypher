LOAD CSV WITH HEADERS FROM 'file:///movies_neo_graph/part-00000-c5c5507e-5501-4adb-87fc-38be1d908076-c000.csv' AS row
MERGE (m:Movie {title: row.title})
MERGE (a:Actor {name: row.actor})

LOAD CSV WITH HEADERS FROM 'file:///movies_neo_graph/part-00000-c5c5507e-5501-4adb-87fc-38be1d908076-c000.csv' AS row
MATCH (m:Movie {title: row.title})
MATCH (a:Actor {name: row.actor})
MERGE (a)-[:ACTED_IN]->(m)

CREATE INDEX FOR (m:Movie) ON m.title;
CREATE INDEX FOR (a:Actor) ON a.name;