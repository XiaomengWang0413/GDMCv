import os
import shutil
import subprocess
import argparse

def run_command(command, env=None, deactivate_env=False):
    """
    A helper function to run shell commands, execute system commands, and handle errors.
    If a specific environment needs to be activated, the command will prepend the environment activation.
    If the current environment needs to be deactivated, set deactivate_env to True.
    """
    if env:
        command = f"source activate {env} && {command}"  # Activate the environment before running the command
    if deactivate_env:
        command += " && source deactivate"  # Deactivate the environment after the command is executed
    try:
        print(f"Running command: {command}")
        subprocess.run(command, shell=True, check=True, executable='/bin/bash')  # Use /bin/bash to support the source command
        print(f"Command completed: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e}")
        exit(1)

def check_file_exists(filepath, file_description="file"):
    """
    Check whether a file exists, and print an error message if not.
    """
    if not os.path.isfile(filepath):
        print(f"{file_description} not found: {filepath}. Please check the path or the output of the previous steps.")
        exit(1)

def main(input_sample, output_sample, threads, length_filter):
    # Define paths
    if output_sample:
        sample_folder = output_sample  # Use the user-specified output folder name
    else:
        sample_name = os.path.splitext(os.path.basename(input_sample))[0]  # Get the input sample file name (without path and extension)
        sample_folder = sample_name  # Default to the input sample name as folder name

    os.makedirs(sample_folder, exist_ok=True)  # Create the output directory for the sample
    genomad_folder = os.path.join(sample_folder, "genomad")
    deepmicroclass_folder = os.path.join(sample_folder, "DeepMicroClass")
    os.makedirs(genomad_folder, exist_ok=True)  # Create the genomad folder within the sample folder
    os.makedirs(deepmicroclass_folder, exist_ok=True)  # Create the DeepMicroClass folder within the sample folder

    # Use the input file name (without extension) for naming
    input_name_no_ext = os.path.splitext(os.path.basename(input_sample))[0]

    # Update paths to include the input file name
    genomad_summary = os.path.join(genomad_folder, f"{input_name_no_ext}_summary")
    genomad_fasta = os.path.join(genomad_summary, f"{input_name_no_ext}_virus.fna")  # Use the actual input file name
    genomad_renamed_fasta = os.path.join(sample_folder, "genomad.fasta")
    sliced_folder = os.path.join(sample_folder, "sliced")  # A folder specifically for saving sliced files
    os.makedirs(sliced_folder, exist_ok=True)  # Ensure the folder exists
    DMC_sliced = os.path.join(sliced_folder, "DMC_sliced")  # Modify the default output file name of slice_fasta_by_names.py
    filtered_fasta = os.path.join(sample_folder, f"{input_name_no_ext}_filtered_{length_filter}.fasta")  # Update file naming format

    # Step 1: Use geNomad for initial prediction of contigs
    command_genomad = f"genomad end-to-end --min-score 0.7 --cleanup --splits {threads} {input_sample} {genomad_folder} ./database/genomad_db"
    run_command(command_genomad, env="genomad", deactivate_env=True)

    # Step 2: Move scaffold_virus.fna to the sample folder and rename it to genomad.fasta
    check_file_exists(genomad_fasta, "geNomad generated viral sequence file")
    shutil.move(genomad_fasta, genomad_renamed_fasta)
    print(f"File successfully moved and renamed to: {genomad_renamed_fasta}")

    # Step 3: Check if genomad.fasta exists and run DeepMicroClass
    check_file_exists(genomad_renamed_fasta, "geNomad output FASTA file")
    command_deepmicroclass = f"DeepMicroClass predict -i {genomad_renamed_fasta} -o {deepmicroclass_folder} -d cuda"
    run_command(command_deepmicroclass, env="DeepMicroClass")  # No need to deactivate environment

    # Step 4: Use slice_dmf_table.py to extract results (run in the base environment)
    dmf_table = os.path.join(deepmicroclass_folder, f"{os.path.basename(genomad_renamed_fasta)}_pred_one-hot_hybrid.tsv")
    check_file_exists(dmf_table, "DeepMicroClass generated DMF table file")
    command_slice_dmf = f"python ./scripts/slice_dmf_table.py -o {deepmicroclass_folder} {dmf_table}"
    run_command(command_slice_dmf, env=None)  # Ensure switching to the base environment

    # Step 5: Use slice_fasta_by_names.py to extract sequences and save outputs into the sliced_fasta folder
    prokaryotic_viruses_txt = os.path.join(deepmicroclass_folder, "sliced_class_ProkaryoticViruses.txt")
    check_file_exists(prokaryotic_viruses_txt, "DeepMicroClass generated classification file")
    command_slice_fasta = f"python ./scripts/slice_fasta_by_names.py {genomad_renamed_fasta} {prokaryotic_viruses_txt} -o {DMC_sliced}"
    run_command(command_slice_fasta, env=None)  # Ensure switching to the base environment

    # Step 6: Check the output file of slice_fasta_by_names.py
    #check_file_exists(sliced_fasta/genomad_sliced/genomad_sliced.fa, "Sliced FASTA file")

    # Step 7: Use seqkit for sequence length filtering and rename output to sample name + length
    command_seqkit_length = f"seqkit seq -m {length_filter} {DMC_sliced}/genomad_sliced.fa -o {filtered_fasta}"
    run_command(command_seqkit_length, env="seqkit", deactivate_env=True)  # Activate seqkit environment and deactivate DeepMicroClass environment
    print(f"Sequence length filtering completed using seqkit, results saved as: {filtered_fasta}")

    print(f"Pipeline completed, final output file: {filtered_fasta}")

if __name__ == "__main__":
    # Use argparse to parse command line arguments
    parser = argparse.ArgumentParser(description="Run geNomad and DeepMicroClass pipeline for viral sequence prediction and extraction.")
    parser.add_argument("-i", "--input", required=True, help="Input file (FASTA format)")
    parser.add_argument("-o", "--output", help="Output folder name")
    parser.add_argument("-t", "--threads", type=int, default=8, help="Number of CPU cores to use (default: 8)")
    parser.add_argument("-l", "--length", type=int, default=2000, help="Minimum sequence length for filtering (default: 2000bp)")
    parser.add_argument("-v", "--version", action="version", version="Pipeline script version 1.1", help="Show script version information")

    args = parser.parse_args()  # Parse command line arguments

    # Call the main function
    main(args.input, args.output, args.threads, args.length)
