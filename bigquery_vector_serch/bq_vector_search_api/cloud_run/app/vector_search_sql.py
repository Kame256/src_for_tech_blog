


def create_vector_search_sql(table,embeddings_data):
    return f"""
WITH temp_table_with_arrays AS (
  SELECT ARRAY<FLOAT64>{embeddings_data} AS float_array
)

SELECT 
  base.filtered_data as filtered_data,
  distance
 FROM
VECTOR_SEARCH(
    TABLE `{table}`,
    'embeddings_data',
    TABLE temp_table_with_arrays,
    'float_array',
    top_k => 5,
    distance_type => 'COSINE',
    options => '{{"use_brute_force":true}}')
ORDER BY distance
LIMIT 5;
"""