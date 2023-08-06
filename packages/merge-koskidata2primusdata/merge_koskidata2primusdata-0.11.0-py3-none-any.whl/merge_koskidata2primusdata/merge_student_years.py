import os
import sys
import glob
import click
import logging
import pandas as pd


def save_merged_df(df, path, file, logger):
    try:
        df.to_excel(
            f"{path}{os.path.sep}raportti_{file['filename'][:-4]}.xlsx", index=False,
        )
        logger.info(
            f"Writing merged data file {path}{os.path.sep}raportti_{file['filename'][:-4]}.xlsx succesfully."
        )
    except Exception as error:
        logger.critical(
            f"Saving merged data to file {path}{os.path.sep}raportti_{file['filename'][:-4]}.xlsx failed. error: {error}"
        )
        pass


@click.command()
@click.argument("koski_input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=True))
@click.argument("primus_data_file", type=click.Path(exists=True))
@click.option(
    "-e", "--primus_encoding", type=click.STRING, default="utf-8-sig", show_default=True
)
@click.option(
    "-E", "--koski_encoding", type=click.STRING, default="utf-8", show_default=True
)
@click.option("-d", "--delimiter", type=click.STRING, default=";", show_default=True)
@click.option("-v", "--validation", type=click.BOOL, default=True, show_default=True)
def main(
    koski_input_path,
    output_path,
    primus_data_file,
    primus_encoding,
    koski_encoding,
    delimiter,
    validation,
):
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Primus/Koski report merging started.")

    files = []

    try:
        for file in glob.glob(f"{koski_input_path}{os.path.sep}*.csv"):
            files.append(
                {"relative_pathname": file, "filename": file.split(os.path.sep)[-1]}
            )
    except Exception as error:
        logger.critical(
            f"Reading input filenames from relative path {koski_input_path} failed. error: {error}"
        )
        sys.exit(0)

    try:
        primus_opphenk = pd.read_csv(
            f"{primus_data_file}", encoding=primus_encoding, delimiter=delimiter, low_memory=False
        )
        logger.info(
            f"Reading Primus data file {primus_data_file} to the dataframe succesfully."
        )
    except Exception as error:
        logger.critical(
            f"Reading primus data from file {primus_data_file} failed. error: {error}"
        )
        sys.exit(0)

    for file in files:
        try:
            df = pd.read_csv(
                file["relative_pathname"],
                encoding=koski_encoding,
                delimiter=delimiter,
                decimal=",",
            )
            try:
                df = df.drop("Hetu")
            except Exception as error:
                pass
            logger.info(
                f"Reading KOSKI data file {file['relative_pathname']} to the dataframe succesfully."
            )
        except Exception as error:
            logger.critical(
                f"Reading koski data from file {koski_input_path}{os.path.sep}{file} failed. error: {error}"
            )
            sys.exit(0)
        try:
            if validation:
                merged = pd.merge(
                    df,
                    primus_opphenk,
                    how="left",
                    left_on="Opiskeluoikeuden tunniste lähdejärjestelmässä",
                    right_on="Korttinumero",
                    validate="1:1",
                )
            else:
                merged = pd.merge(
                    df,
                    primus_opphenk,
                    how="left",
                    left_on="Opiskeluoikeuden tunniste lähdejärjestelmässä",
                    right_on="Korttinumero",
                )
            merged = merged.drop(columns=["Korttinumero"], axis=1)
            student_dates_columns = [name for name in merged.columns if "(pv)" in name]
            for column in student_dates_columns:
                merged[column.replace("(pv)", "(v)")] = merged[column] / 365
            save_merged_df(merged, output_path, file, logger)
        except Exception as error:
            logger.critical(
                f"Merging KOSKI data and Primus data failed. error: {error}"
            )
            duplicates = df[
                df.duplicated("Opiskeluoikeuden tunniste lähdejärjestelmässä")
            ]["Opiskeluoikeuden tunniste lähdejärjestelmässä"].tolist()
            logger.info(f"Duplicated identifiers on Koski report: {duplicates}")
            duplicates = primus_opphenk[primus_opphenk.duplicated("Korttinumero")][
                "Korttinumero"
            ].tolist()
            logger.info(f"Duplicated identifiers on Primus report: {duplicates}")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter

