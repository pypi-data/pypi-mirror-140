from pyspark.sql import DataFrame as SparkDF
from pandas import DataFrame as PandasDF
from pandas import concat
from pyspark.sql import functions as f
from multiprocessing.pool import ThreadPool
from itertools import chain
from ...collections import OrderedSet



def union(*args, n_jobs):
	"""
	takes multiple spark DataFrames and produces the union
	:type args: SparkDF or PandasDF or list[SparkDF] or list[PandasDF]
	:type n_jobs: int
	:rtype: DataFrame
	"""
	if len(args) == 1 and isinstance(args[0], list):
		args = args[0]

	if all([isinstance(x, SparkDF) for x in args]):
		global_data_type = 'spark_df'
	elif all([isinstance(x, PandasDF) for x in args]):
		global_data_type = 'pandas_df'
	else:
		raise TypeError('All dataframes should be the same type of DataFrame.')

	def _get_columns(x):
		if x is None:
			return []
		else:
			return list(x.columns)

	def _add_columns(_data, _all_columns):
		"""
		adds empty columns to _data for the columns it is missing from among all_columns
		:type _data: DataFrame
		:rtype: DataFrame
		"""
		if _data is None:
			return None

		_missing_columns = [_col for _col in _all_columns if _col not in _data.columns]
		if global_data_type == 'spark_df':
			return _data.select(*_data.columns, *[f.lit(None).alias(col) for col in _missing_columns])
		elif global_data_type == 'pandas_df':
			_result = _data.copy()
			for col in _missing_columns:
				_result[col] = None
			return _result
		else:
			raise TypeError(f'Unsupported data type: {type(_data)}')

	if n_jobs > 1:
		pool = ThreadPool(n_jobs)
		column_lists = pool.map(_get_columns, args)
		all_columns = OrderedSet(chain(*column_lists))
		df_list = pool.map(lambda x: _add_columns(x, _all_columns=all_columns), args)
	else:
		pool = None
		column_lists = [_get_columns(x) for x in args]
		all_columns = OrderedSet(chain(*column_lists))
		df_list = [_add_columns(x, _all_columns=all_columns) for x in args]

	def _union_by_name(_df1, _df2):
		"""
		orders _df2 columns in the same way as _df1 to make union easy
		:type _df1: DataFrame
		:type _df2: DataFrame
		:rtype: DataFrame
		"""
		if _df1 is None or _df1 is False:
			return _df2
		elif _df2 is None or _df2 is False:
			return _df1

		if global_data_type == 'spark_df':
			# make sure columns are the same type, otherwise cast them into string
			dtypes1 = {col: dtype for col, dtype in _df1.dtypes}
			dtypes2 = {col: dtype for col, dtype in _df2.dtypes}

			common_columns = set(dtypes1.keys()).intersection(dtypes2.keys())
			different_columns = []
			for col in common_columns:
				t1 = dtypes1[col].lower()
				t2 = dtypes2[col].lower()
				if t1 != t2:
					if t1 == 'string' or t2 == 'string' or t1.startswith('array') or t2.startswith('array') or t1.startswith('struct') or t2.startswith('struct'):
						different_columns.append(col)
			other_columns1 = [col for col in dtypes1.keys() if col not in different_columns]
			other_columns2 = [col for col in dtypes2.keys() if col not in different_columns]

			_df1 = _df1.select(*other_columns1, *[f.col(col).cast('string').alias(col) for col in different_columns])
			_df2 = _df2.select(*other_columns2, *[f.col(col).cast('string').alias(col) for col in different_columns])

			return _df1.union(_df2.select(*_df1.columns))

		elif global_data_type == 'pandas_df':
			return concat([_df1, _df2])

		else:
			raise TypeError(f'Unsupported types: {type(_df1)} and {type(_df2)}')

	def _reduce_in_half(_df_list):
		# unions half of the list with the other half and reduces the list to half its original size
		if len(_df_list) % 2 == 1:
			_new_list = _df_list + [None]
		else:
			_new_list = _df_list

		pairs = []
		for i in range(len(_new_list) // 2):
			pairs.append((_new_list[i*2], _new_list[i*2 + 1]))

		if pool is None:
			result = [_union_by_name(pair[0], pair[1]) for pair in pairs]
		else:
			result = pool.map(lambda pair: _union_by_name(pair[0], pair[1]), pairs)
		return result

	def _union(_df_list):
		"""
		:type _df_list: list[PandasDF] or list[SparkDF]
		:rtype: PandasDF or SparkDF
		"""
		result = _df_list.copy()
		while len(result) > 1:
			result = _reduce_in_half(result)
		return result[0]

	return _union(df_list)
