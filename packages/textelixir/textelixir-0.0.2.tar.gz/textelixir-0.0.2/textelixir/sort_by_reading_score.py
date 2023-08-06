from glob import glob
import textstat



files = glob('sentences_b*/*.txt')
for f in files:
    scores = {}
    with open(f, 'r', encoding='utf-8') as file_in:
        lines = file_in.read().splitlines()
    for line in lines:
        cit, *sent = line.split('\t')
        sent = ' '.join(sent)
        score = textstat.flesch_reading_ease(sent)
        scores[line] = score
    
    sorted_sents = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    with open(f, 'w', encoding='utf-8') as file_out:
        print(f)
        for i in sorted_sents:
            print(i[0], file=file_out)