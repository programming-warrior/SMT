from PhraseExtractor import PhraseExtractor

def main(): 
    extractor = PhraseExtractor(
        src_file="./english.txt",
        tgt_file="./hindi.txt",
        align_file="./eng-hin-align.txt",
        output_file="./output.txt"
    )
    extractor.run()

if __name__ == "__main__":
    main()