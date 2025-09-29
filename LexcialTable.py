from collections import defaultdict

class LexicalTable:
    def __init__(self, src_file_path, tgt_file_path, aligned_file_path, output_file_path):
        self.src_count = defaultdict(int)  # counts of src words
        self.tgt_count = defaultdict(int)  # counts of tgt words
        self.alignment_map = defaultdict(lambda: defaultdict(int))  # src -> {tgt -> count}

        self.src_file_path = src_file_path
        self.tgt_file_path = tgt_file_path
        self.aligned_file_path = aligned_file_path
        self.output_file_path = output_file_path

    def getWordAlignmentCount(self, src_line, tgt_line, align_line):
        src_tokens = src_line.strip().split(' ')
        tgt_tokens = tgt_line.strip().split(' ')
        align_tokens = align_line.strip().split(' ')

        for align_token in align_tokens:
            # source_word_idx-target_word_idx (e.g., 0-1)
            src_word_idx, tgt_word_idx = map(int, align_token.split('-'))
            src_word = src_tokens[src_word_idx]
            tgt_word = tgt_tokens[tgt_word_idx]

            # update counts
            self.src_count[src_word] += 1
            self.tgt_count[tgt_word] += 1
            self.alignment_map[src_word][tgt_word] += 1

        # TODO: NULL EDGE-CASE HANDLING

        return

    def saveLexicalTable(self):
        output_file_path = self.output_file_path + ".s2d"
        output_file_path_inv = self.output_file_path + ".d2s"

        with open(output_file_path, "w", encoding="utf-8") as o_file, \
             open(output_file_path_inv, "w", encoding="utf-8") as o_file_inv:

            for src_word, tgt_dict in self.alignment_map.items():
                for tgt_word, total_count in tgt_dict.items():
                    source_count = self.src_count[src_word]
                    target_count = self.tgt_count[tgt_word]

                    # avoid division by zero
                    if source_count > 0:
                        # P(t|s)
                        trans_prob = total_count / source_count
                        o_file.write(f"{tgt_word} {src_word} {trans_prob:.6f}\n")

                    if target_count > 0:
                        # P(s|t)
                        trans_prob_inv = total_count / target_count
                        o_file_inv.write(f"{src_word} {tgt_word} {trans_prob_inv:.6f}\n")

    def run(self):
        with open(self.src_file_path, "r", encoding="utf-8") as i_src_file, \
             open(self.tgt_file_path, "r", encoding="utf-8") as i_tgt_file, \
             open(self.aligned_file_path, "r", encoding="utf-8") as i_align_file:

            for src_line, tgt_line, align_line in zip(i_src_file, i_tgt_file, i_align_file):
                self.getWordAlignmentCount(src_line, tgt_line, align_line)

        self.saveLexicalTable()
