
import sys

class PhraseInfo:
    def __init__(self):
        self.src_tokens = []
        self.tgt_tokens = []
        self.src_to_tgt = []
        self.src_aligned_count = []
        self.tgt_to_src = []
        self.tgt_aligned_count = []


    def create(self, src, tgt, align): 
        self.src_tokens = src.split(' ')
        self.tgt_tokens = tgt.split(' ')
        self.src_to_tgt= [set() for _ in range(len(self.src_tokens))]
        self.src_aligned_count = [ 0 for _ in range(len(self.src_tokens))]
        self.tgt_to_src = [set() for _ in range(len(self.tgt_tokens))]
        self.tgt_aligned_count = [ 0 for _ in range(len(self.tgt_tokens))]


        for align_pair in align.split(' '):
            src_idx, tgt_idx = map(int, align_pair.split('-'))
            self.src_to_tgt[src_idx].add(tgt_idx)
            self.tgt_to_src[tgt_idx].add(src_idx)
            self.src_aligned_count[src_idx] = self.src_aligned_count[src_idx] + 1
            self.tgt_aligned_count[tgt_idx] = self.tgt_aligned_count[tgt_idx] + 1



class MEOrdering:
    def __init__(self, src_file, tgt_file, align_file, output_file):
        self.src_file = src_file
        self.tgt_file = tgt_file        
        self.align_file = align_file
        self.output_file = output_file

    def findTgtPhrase(self, phrase_info: PhraseInfo, src_start, src_end):
        tgt_start = sys.maxsize
        tgt_end = -1
        tgt_src_aligned = phrase_info.tgt_aligned_count.copy()
        for src_idx in range(src_start, src_end+1):
            for tgt_idx in phrase_info.src_to_tgt[src_idx]:
                if tgt_idx < tgt_start:
                    tgt_start = tgt_idx
                if tgt_idx > tgt_end:
                    tgt_end = tgt_idx
                
                tgt_src_aligned[tgt_idx] = tgt_src_aligned[tgt_idx] - 1

        if tgt_end >= 0: 
            #check if target phrase is aligned to any source word outside the source phrase
            for tgt_idx in range(tgt_start, tgt_end+1):
                if tgt_src_aligned[tgt_idx] > 0:
                    return (-1, -1)
                
            return (tgt_start, tgt_end)

        return (-1, -1)         

    def saveFeatures(self, out_f, phrase_info: PhraseInfo, src_start1, src_end1, src_start2, src_end2, tgt_start1, tgt_end1, tgt_start2, tgt_end2, orientation):
        out_f.write(f"{orientation} ||| SLL={phrase_info.src_tokens[src_start1]} SLR={phrase_info.src_tokens[src_end1]} TLL={phrase_info.tgt_tokens[tgt_start1]} TLR={phrase_info.tgt_tokens[tgt_end1]} SRL={phrase_info.src_tokens[src_start2]} SRR={phrase_info.src_tokens[src_end2]} TRL={phrase_info.tgt_tokens[tgt_start2]} TRR={phrase_info.tgt_tokens[tgt_end2]}\n")


    def extract_features(self, phrase_info: PhraseInfo, out_f):
        for span in range(2, len(phrase_info.src_tokens)):
            for start in range(len(phrase_info.src_tokens)-span+1):
                end = start + span - 1
                for mid in range(start+1, end): 
                    left_tgt_start, left_tgt_end = self.findTgtPhrase(phrase_info, start, mid-1)
                    if left_tgt_start < 0 or left_tgt_end < 0:
                        continue
                    right_tgt_start, right_tgt_end = self.findTgtPhrase(phrase_info, mid, end)
                    if right_tgt_start < 0 or right_tgt_end < 0:
                        continue   

                    #check the orientation
                    if left_tgt_end < right_tgt_start:
                        gap_count=0 
                        is_unaligned = True
                        for idx in  range(left_tgt_end+1, right_tgt_start):
                            if phrase_info.tgt_aligned_count[idx] > 0:
                                is_unaligned = False
                                break
                            gap_count = gap_count + 1
                        if not is_unaligned or gap_count > 4:
                            continue

                        orientation = "STRAIGHT"

                    elif left_tgt_end >= right_tgt_start:
                        gap_count=0
                        is_unaligned = True
                        for idx in  range(right_tgt_end+1, left_tgt_start):
                            if phrase_info.tgt_aligned_count[idx] > 0:
                                is_unaligned = False
                                break
                            gap_count = gap_count + 1
                        if not is_unaligned or gap_count > 4:
                            continue

                        orientation = "INVERTED"

                    self.saveFeatures(out_f, phrase_info, start, mid-1, mid, end, left_tgt_start, left_tgt_end, right_tgt_start, right_tgt_end, orientation)

       
        

    def run(self): 
        try: 
            with open(self.src_file, 'r', encoding='utf-8') as src_f, open(self.tgt_file, 'r', encoding='utf-8') as tgt_f, open(self.align_file, 'r', encoding='utf-8') as align_f, open(self.output_file, 'w', encoding='utf-8') as out_f:
                src_lines = src_f.readlines()
                tgt_lines = tgt_f.readlines()
                align_lines = align_f.readlines()
                if len(src_lines)==0 or len(tgt_lines)==0 or len(align_lines)==0:
                    print("One of the input files is empty.")
                    return

                for src, tgt, align in zip(src_lines, tgt_lines, align_lines):
                    phrase_info = PhraseInfo()
                    phrase_info.create(src.strip(), tgt.strip(), align.strip())
                    self.extract_features(phrase_info, out_f)
        except Exception as e:
            print(f"Error: {e}")
            return
