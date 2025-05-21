import os
import re
import pandas as pd

path = ''  # directory for redcap files. option: Change to YAML config
path1 = ''  # directory for GH file: Change to YAML config
path2 = ''  # directory for 'participants_conditions_redcap_summary.xlsx': Change to YAML config


def check_differences_dataframes(path1, path2):
    df1 = pd.read_excel(path1)
    df2 = pd.read_excel(path2)
    df1 = df1.drop_duplicates()  # GH
    column_df1 = set(df1.iloc[:, 0])
    column_df2 = set(df2.iloc[:, 0])

    differences = column_df1 - column_df2
    print(differences)


def check_duplicates(filepath1, subset):
    issues = []

    df = pd.read_excel(filepath1)
    duplicates = df.loc[df.duplicated(subset=subset, keep='first')].copy()
    duplicates["issue_type"] = "duplication"

    if duplicates.empty:
        print(f"\n ✔ | Validation of duplications passed: No duplicated rows were found in current table.")
    else:
        print(f"\n❌ | {len(duplicates)} Duplicated values have been found in table:\n {duplicates}")
        issues.append(duplicates)


def condition_cleaning_column(column):
    cleaned = column.lower()
    cleaned = re.sub(r'\(.*?\)', '', cleaned)
    cleaned = re.sub(r'[^a-z\s]', '', cleaned)
    return "condition" in cleaned


def study_id_cleaning_column(column):
    cleaned = column.lower()
    cleaned = re.sub(r'\(.*?\)', '', cleaned)
    cleaned = re.sub(r'[^a-z\s]', '', cleaned)
    return "study id" in cleaned


def gather_files(directory):
    column_with_duplications = []

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)

            condition_columns = [col for col in df.columns if condition_cleaning_column(col)]

            if 'record_id' in df.columns and 'study_id' in df.columns:
                print(f"Option 1: {file}")  # For this file, use only "study_id" column
                df = df.rename(columns={'study_id': 'participant_identifier'})
                df['condition'] = df[condition_columns].any(axis=1).astype(int)
                participants_conditions = df[['participant_identifier', 'condition']]
                column_with_duplications.append(participants_conditions)

            elif 'record_id' in df.columns:
                print(f"Option 2: {file}")  # For these files, use "record_id" column
                df = df.rename(columns={'record_id': 'participant_identifier'})
                df['condition'] = df[condition_columns].any(axis=1).astype(int)
                participants_conditions = df[['participant_identifier', 'condition']]
                column_with_duplications.append(participants_conditions)

            elif 'Record ID' in df.columns:
                record_id_values = df['Record ID'].astype(str).str.strip()
                if (record_id_values.str.len() > 6).all():
                    print(f"Option 3a:  {file} ")  # 'Record ID'

                    df = df.rename(columns={'Record ID': 'participant_identifier'})
                    df['condition'] = df[condition_columns].any(axis=1).astype(int)
                    participants_conditions = df[['participant_identifier', 'condition']]
                    column_with_duplications.append(participants_conditions)

                else:
                    print(f"Option 3b:  {file}")  # 'Record ID'
                    participant_columns = [col for col in df.columns if study_id_cleaning_column(col)]
                    df['participant_identifier'] = df[participant_columns]
                    df['condition'] = df[condition_columns].any(axis=1).astype(int)
                    participants_conditions = df[['participant_identifier', 'condition']]
                    column_with_duplications.append(participants_conditions)

    # print(column_with_duplications)
    merged_conditions_duplications = pd.concat(column_with_duplications, ignore_index=True)
    merged_conditions_duplications = merged_conditions_duplications.drop_duplicates()
    merged_conditions_duplications.to_excel("participants_conditions_redcap_summary.xlsx", index=False)
    print("Saving merged file")


def main():
    gather_files(path)
    check_duplicates(path2, "record_id")  # Change to column_name when is required to check another column's file.
    check_differences_dataframes(path1, path2)


if __name__ == '__main__':
    main()
