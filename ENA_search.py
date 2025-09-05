import os
import requests
import argparse
import csv

def download_fastq(run_accession, output_dir):
    
    search_url = "https://www.ebi.ac.uk/ena/portal/api/search"
    params = {
        'result': 'read_run',
        'query': f'accession={run_accession}',
        'fields': 'fastq_ftp',
        'format': 'tsv',
        'limit': 0
    }

    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch data for run accession: {run_accession}")
        return

    fastq_files = []
    reader = csv.DictReader(response.text.splitlines(), delimiter='\t')
    for row in reader:
        if 'fastq_ftp' in row and row['fastq_ftp']:
            fastq_files.extend(row['fastq_ftp'].split(';'))

    if not fastq_files:
        print(f"No FASTQ files found for run accession: {run_accession}")
        return

    # Make sure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Download FASTQ files
    for fastq_url in fastq_files:
        if not fastq_url.startswith("ftp://") and not fastq_url.startswith("https://"):
            fastq_url = "https://" + fastq_url
        fastq_filename = os.path.join(output_dir, os.path.basename(fastq_url))
        print(f"Downloading {fastq_url} to {fastq_filename}")
        response = requests.get(fastq_url, stream=True)
        if response.status_code == 200:
            with open(fastq_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            print(f"Failed to download {fastq_url}")

    print("Download completed.")

def main():
    parser = argparse.ArgumentParser(description="Download FASTQ files from ENA using run accession.")
    parser.add_argument("run_accession", type=str, help="Run accession number to search in ENA")
    parser.add_argument("output_dir", type=str, help="Output directory to save the downloaded FASTQ files")

    args = parser.parse_args()

    download_fastq(args.run_accession, args.output_dir)

if __name__ == "__main__":
    main()

