import pandas as pd
import json5


def find_value_block(key_block, value_map):
    for relationship in key_block['Relationships']:
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                return value_map[value_id]
    return None

def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X '
    return text.strip()
def get_kv_relationship(key_map, value_map, block_map):
    kvs = {}
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        val = get_text(value_block, block_map)
        kvs[key] = val
    return kvs


def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    scores = []
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        rows[row_index] = {}

                    scores.append(str(cell['Confidence']))
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows, scores


def generate_table_csv(table_result, blocks_map, table_index):
    rows, scores = get_rows_columns_map(table_result, blocks_map)
    table_id = 'Table_' + str(table_index)
    csv = 'Table: {0}\n\n'.format(table_id)

    for row_index, cols in rows.items():
        for col_index, text in cols.items():
            csv += '{}'.format(text) + ","
        csv += '\n'

    csv += '\n\n Confidence Scores % (Table Cell) \n'
    cols_count = 0
    for score in scores:
        cols_count += 1
        csv += score + ","
    csv += '\n\n\n'

    return csv

def generate_table_dataframes(table_blocks, blocks_map):
    table_dataframes = []

    for index, table in enumerate(table_blocks):
        df = generate_table_dataframe(table, blocks_map, index + 1)
        table_dataframes.append(df)

    return table_dataframes


def generate_table_dataframe(table_block, blocks_map, table_index):
    rows, _ = get_rows_columns_map(table_block, blocks_map)
    table_data = []

    if rows:
        # Initialize cols with the first row's columns
        first_row_cols = rows[1]  # Assuming the first row is at index 1
        column_headers = [first_row_cols[col_index] for col_index in sorted(first_row_cols.keys())]
        for row_index, cols in rows.items():
            if row_index != 1:  # Skip the first row if it's column headers
                row_data = {}
                for col_index, text in cols.items():
                    if col_index < len(column_headers):
                        row_data[column_headers[col_index - 1]] = text
                table_data.append(row_data)

    df = pd.DataFrame(table_data)
    return df

def process_textract_response(textract_response):
    try:
        blocks = textract_response['Blocks']
        blocks_map = {}
        key_map = {}
        value_map = {}
        table_blocks = []

        for block in blocks:
            blocks_map[block['Id']] = block
            if block['BlockType'] == "KEY_VALUE_SET":
                if 'KEY' in block['EntityTypes']:
                    key_map[block['Id']] = block
                else:
                    value_map[block['Id']] = block
            if block['BlockType'] == "TABLE":
                table_blocks.append(block)

        kvs = get_kv_relationship(key_map, value_map, blocks_map)

        # table_dataframes = generate_table_dataframes(table_blocks, blocks_map)
        data_frames = generate_table_dataframes(table_blocks, blocks_map)

        table_strings = ['' for _ in range(5)]
        table_count = 0

        for df in data_frames:
            if len(df.columns) > 2:
                table_string = ''
                for index, row in df.iterrows():
                    for column in df.columns:
                        table_string += f"{column}: {row[column]}\n"
                    table_string += "\n"
                table_strings[table_count] = table_string
                table_count += 1
                if table_count >= 5:
                    break

        return {
            'kvs': kvs,
            'table_1': table_strings[0],
            'table_2': table_strings[1],
            'table_3': table_strings[2],
            'table_4': table_strings[3],
            'table_5': table_strings[4]
        }
    except:
        return {
            'kvs': {},
            'table_1': '',
            'table_2': '',
            'table_3': '',
            'table_4': '',
            'table_5': ''
        }