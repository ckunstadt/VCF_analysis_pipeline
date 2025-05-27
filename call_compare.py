import argparse
import subprocess
# Cameron Kunstadt
# Etalon Diagnostics
# May-6-2025

parser = argparse.ArgumentParser(description="This script compares homozygous calls between two vcfs, returns list and stats")
parser.add_argument('-f1', '--file1')
parser.add_argument('-f2', '--file2') # At some point will need to make the number of files flexible but this is fine
parser.add_argument('-o', '--output')
args = parser.parse_args()

shared_alt_homo_alleles = 0
position_list = []

def is_homo(info):
    '''Returns the HOMO value given the INFO value of a vcf line'''
    if "1/1" in info:
        return True
    else:
        return False

with open(args.file1, 'r') as file1, open(args.file2, 'r') as file2, open(args.output, 'w') as outfile:
    while True:
        f1_line = file1.readline()

        f2_line = file2.readline()

        if f1_line == "": # Break if EOF
            break
        elif f1_line[0] == "#" and f2_line[0] == "#": # Ignore header lines
            outfile.write(f1_line)
            continue
        elif f1_line[0] != "#" and f2_line[0] == "#":
            while True:
                test_line = file2.readline()

                if test_line[0] != "#":
                    break
        elif f2_line[0] != "#" and f1_line[0] == "#":
            while True:
                test_line = file1.readline()
                
                if test_line[0] != "#":
                    break
                outfile.write(f1_line)
        else:
            f1_list = f1_line.strip().split('\t')
            f2_list = f2_line.strip().split('\t')

            chrom1 = f1_list[0]
            pos1 = f1_list[1]
            id1 = f1_list[2]
            ref1 = f1_list[3]
            alt1 = f1_list[4]

            chrom2 = f2_list[0]
            pos2 = f2_list[1]
            id2 = f2_list[2]
            ref2 = f2_list[3]
            alt2 = f2_list[4]

            if chrom1 != chrom2 or pos1 != pos2 or id1 != id2: # Lines compared should ALWAYS share these in common
                print ("THESE FILES DO NOT HAVE THE SAME SNPS IN THE SAME ORDER!!!")
                break

            if alt1 == alt2 and alt1 != '.' and alt2 != '.' and (is_homo(f1_list[10]) == False) and (is_homo(f2_list[10]) == False):
                shared_alt_homo_alleles += 1
                position_list.append([chrom1, pos1, id1])
                outfile.write(f1_line)


print(shared_alt_homo_alleles)






