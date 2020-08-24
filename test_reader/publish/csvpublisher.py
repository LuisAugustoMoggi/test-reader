import os
import csv


class CsvPublisher:

    @staticmethod
    def publish(values):
        result_dir = os.environ.get("RESULT_DIR")
        with open(result_dir + 'test_reader_result.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in values:
                writer.writerow(row)

