from PhraseExtractor import PhraseExtractor
from LexcialTable import LexicalTable
from ScorePhrase import ScorePhrase
from MEOrdering import MEOrdering

def main(): 
    extractor = PhraseExtractor(
        src_file="training-data/english.txt",
        tgt_file="training-data/hindi.txt",
        align_file="training-data/eng-hin-align.txt",
        output_file="output/phrase-table"
    )
    # extractor.run()

    lex_generator = LexicalTable(
        src_file_path="training-data/english.txt",
        tgt_file_path="training-data/hindi.txt",
        aligned_file_path="training-data/eng-hin-align.txt",
        output_file_path="output/lex"
    )


    # lex_generator.run()
    score_phrase= ScorePhrase(phrase_table_file="output/phrase-table", lex_file="output/lex.s2d", output_file="output/score")

    # score_phrase.run()

    me_ordering = MEOrdering(
        src_file="training-data/english.txt",
        tgt_file="training-data/hindi.txt",
        align_file="training-data/eng-hin-align.txt",
        output_file="output/me_ordering1"
    )
    me_ordering.run()
    return

if __name__ == "__main__":
    main()