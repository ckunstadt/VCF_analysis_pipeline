import argparse
import subprocess
# Cameron Kunstadt
# Etalon Diagnostics
# May-9-2025

parser = argparse.ArgumentParser(description="This script compares homozygous calls between two vcfs, returns list and stats")
parser.add_argument('-f1', '--file1')
parser.add_argument('-f2', '--file2') # At some point will need to make the number of files flexible but this is fine
parser.add_argument('-c', '--control', nargs='+', type=str)
parser.add_argument('-n', '--name', default="experiment")
args = parser.parse_args()

####################################################################

def run_intersect(file1, file2, dir):
    '''Runs bcftools intersection command and outputs into given directory'''
    subprocess.run(["bcftools", "isec", "-p", f"{dir}/", f"{file1}", f"{file2}"])

def run_merge(file_list, output):
    files = " ".join(file_list)
    subprocess.run(f"bcftools concat {files} -o {output}", shell=True, check=True)

def run_compression(file):
    subprocess.run(f"bgzip -c {file} > {file}.gz", shell=True)

def run_index(file):
    subprocess.run(["tabix", f"{file}"])

def run_call_compare(file1, file2, output):
    subprocess.run(["python", "call_compare.py", "-f1", f"{file1}", "-f2", f"{file2}", "-o", f"{output}"])

def run_compare_to_WT(file1, file2, output):
    subprocess.run(["python", "compare_to_WT.py", "-f1", f"{file1}", "-f2", f"{file2}", "-o", f"{output}"])

def run_sort(file, outfile):
    subprocess.run(f"bcftools sort {file} -o {outfile}", shell=True, check=True)

###################################################################


# THIS ASSUMES FILES ARE GZIPPED AND INDEX AT THE BEGINNING, NOT GREAT TO ASSUME
run_intersect(args.file1, args.file2, f'{args.name}_initial_shared_homo')
#just get rid of headers somehow before this!!!!
run_call_compare(f'{args.name}_initial_shared_homo/0002.vcf', f'{args.name}_initial_shared_homo/0003.vcf', f"{args.name}_shared_homo_mut.vcf")
run_compression(f"{args.name}_shared_homo_mut.vcf")
run_index(f"{args.name}_shared_homo_mut.vcf.gz")

removal_file_list = []
# now for creating a list of markers to remove
for i, file in enumerate(args.control): # the args.control needs to be in a list format!!, also the files should all be compressed and indexed by this point
    run_intersect(f"{args.name}_shared_homo_mut.vcf.gz", file, f"temp_dir_{i}")
    run_compare_to_WT(f"temp_dir_{i}/0002.vcf", f"temp_dir_{i}/0003.vcf", f"for_removal_{i}.vcf")
    run_compression(f"for_removal_{i}.vcf")
    run_index(f"for_removal_{i}.vcf.gz")
    removal_file_list.append(f"for_removal_{i}.vcf.gz")

run_merge(removal_file_list, "full_removal.vcf.gz")
run_sort("full_removal.vcf.gz", "full_removal_sorted.vcf.gz")
run_index("full_removal_sorted.vcf.gz")
run_intersect(f"{args.name}_shared_homo_mut.vcf.gz", "full_removal_sorted.vcf.gz", "final_intersect")

subprocess.run(["cp", "final_intersect/0000.vcf", f"intronic_and_exonic_{args.name}.vcf"])





