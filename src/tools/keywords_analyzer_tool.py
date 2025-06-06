import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Type
from pydantic import BaseModel, Field, PrivateAttr
from crewai.tools.base_tool import BaseTool
import argparse
from pathlib import Path
import nltk
import textract
nltk.download('averaged_perceptron_tagger_eng')
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
nlp = spacy.load('en_core_web_sm')


def write_file(file_name, write_mode, write_string):
    '''
    This function writes the Resume and JD comparison result to an output file.
    Input: Output file name, Write mode, Write string
    Output: Writes result to the output file
    '''
    output_file = open(file_name, write_mode)
    output_file.write(write_string)
    output_file.write('\n\n')
    output_file.write('-------------------------------------------------------------------------')
    output_file.write('\n\n')
    output_file.close()


def clean_text(text):
    '''
    This function cleans non-ASCII special characters from input text data.
    Input: Text string
    Output: Text string
    '''
    import re
    cleaned_data = re.sub(r'[^a-zA-Z0-9\s\/]', '', text)
    cleaned_data = cleaned_data.replace('/', ' ')
    return cleaned_data

def filter_token_tag(tagged_token_list, filter_tag_list):
    '''
    This function filters the tagged token list present in the filter tag list.
    Input: Tagged token list, filter tag list
    Output: List containing tokens corresponding to tags present in the filter tag list
    '''
    filtered_token_list = [t[0] for t in tagged_token_list if t[1] in filter_tag_list]
    filtered_token_list = [str(item) for item in filtered_token_list]
    return filtered_token_list

def unique_tokens(token_list):
    '''
    This function removes duplicate tokens from the input token list.
    Input: Token list
    Output: Unique token list
    '''
    unique_token_list = []
    for x in token_list:
        x = x.lower()
        if x not in unique_token_list:
            unique_token_list.append(x)
    return unique_token_list

def nltk_tokenizer(text):
    '''
    This function uses the NLTK tokeniser to tokenise the input text.
    Input: Text string
    Output: Tokens
    '''
    nltk.download('punkt')
    from nltk import word_tokenize
    tokens = word_tokenize(text)
    #tokens = text.split()
    return tokens

def nltk_pos_tag(token_list):
    '''
    This function uses the NLTK parts of speech tagger to apply tags to the input token list.
    Input: Token List
    Output: Tagged token list
    '''
    nltk.download('averaged_perceptron_tagger')
    from nltk import pos_tag
    tagged_list = pos_tag(token_list)
    return tagged_list

def nltk_stopwords_removal(token_list):
    '''
    This function removes stopwords from the input token list using the NLTK stopwords dictionary.
    Input: Token List
    Output: Stopwords filtered list
    '''
    nltk.download('stopwords')
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
    stopwords_filtered_list = [w for w in token_list if w not in stop_words]
    return stopwords_filtered_list

def nltk_keywords(data):
    '''
    This function contains the NLTK pipeline to detect keywords from input text data.
    Input: Text data
    Output: Keywords
    '''
    data = clean_text(data)
    tokens = nltk_tokenizer(data)
    pos_tagged_tokens = nltk_pos_tag(tokens)
    keywords = filter_token_tag(pos_tagged_tokens, ['NNP', 'NN', 'VBP', 'JJ'])
    keywords = nltk_stopwords_removal(keywords)
    keywords = unique_tokens(keywords)
    #print('NLTK Keywords: ', keywords)
    return keywords



def spacy_tokenizer(text):
    '''
    This function uses the spacy tokeniser to tokenise the input text.
    Input: Text string
    Output: Tokens
    '''
    tokens = nlp(text)
    #tokens = text.split()
    return tokens

def spacy_pos_tag(token_list):
    '''
    This function uses the spacy parts of speech tagger to apply tags to the input token list.
    Input: Token List
    Output: Tagged token list
    '''
    tagged_list = []
    for tok in token_list:
        tagged_list.append((tok,tok.tag_))
    return tagged_list

def spacy_stopwords_removal(token_list):
    '''
    This function removes stopwords from the input token list using the spacy stopwords dictionary.
    Input: Token List
    Output: Stopwords filtered list
    '''
    stop_words = nlp.Defaults.stop_words
    stopwords_filtered_list = [w for w in token_list if w not in stop_words]
    return stopwords_filtered_list

def spacy_keywords(data):
    '''
    This function contains the spacy pipeline to detect keywords from input text data.
    Input: Text data
    Output: Keywords
    '''
    data = clean_text(data)
    tokens = spacy_tokenizer(data)
    pos_tagged_tokens = spacy_pos_tag(tokens)
    keywords = filter_token_tag(pos_tagged_tokens, 'NNP')
    keywords = spacy_stopwords_removal(keywords)
    keywords = unique_tokens(keywords)
    #print('Spacy Keywords: ', keywords)
    return keywords



class KeywordsAnalyzeInput(BaseModel):
    resume: str = Field(
        None, description="Applicant resume"
    )
    job_description: str = Field(
        None, description="Job Description"
    )

# based on https://github.com/sumitprdrsh/Resume_Compatibility
class KeywordsAnalyzerTool(BaseTool):
    name: str = "keywords_analyzer_tool"
    description: str = ("Performs keywords analysis comparing the job description and the resume to evaluate the "
                        "matching words. It returns a table with tree columns, ID, JD Keyword, JD-Resume Match "
                        "Result. Iyt also returns Match percentage based on Keywords and Match percentage based on "
                        "Cosine Similarity")
    args_schema: Type[KeywordsAnalyzeInput] = KeywordsAnalyzeInput

    def _run(self, resume: str, job_description: str) -> str:

        # keywords extraction from job description
        keywords_jd = spacy_keywords(job_description)
        # keywords_jd = nltk_keywords(job_description)


        # keywords extraction from resume
        # keywords_resume = nltk_keywords(data_resume)
        keywords_resume = spacy_keywords(resume)

        # ----------------Matching Keywords between JD and Resume-----------------------
        # Creating a table showing Match Result between JD and Resume
        jd_keywords_in_resume_table = []
        for word in keywords_jd:
            if word in keywords_resume:
                match_result = [word, 'Match']
            else:
                match_result = [word, 'No Match']
            jd_keywords_in_resume_table.append(match_result)

        from tabulate import tabulate
        ret_val = "Comparing Resume and Job Description:"
        ret_val += "\n" + tabulate(jd_keywords_in_resume_table, headers=['ID', 'JD Keyword', 'JD-Resume Match Result'],
                       showindex='always', tablefmt='psql')

        # calculating the percentage of the match result
        jd_keywords_in_resume_list = [w for w in keywords_jd if w in keywords_resume]
        jd_keywords_in_resume_list_count = len(jd_keywords_in_resume_list)
        jd_keywords_count_total = len(keywords_jd)

        match_percentage = (jd_keywords_in_resume_list_count / jd_keywords_count_total) * 100
        match_percentage = round(match_percentage, 2)  # round to two decimal
        ret_val += "\n" + f"Match percentage based on Keywords: {match_percentage}%"

        # calculating the cosine similarity between JD and Resume Keywords----------------
        text = [job_description, resume]
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(text)
        # get the match percentage
        match_percentage = cosine_similarity(count_matrix)[0][1] * 100
        match_percentage = round(match_percentage, 2)  # round to two decimal
        ret_val += "\n" + f"match percentage based on cosine similarity: {match_percentage}%"

        ret_val += "\n" + 'Try to include unmatched keywords in your Resume to improve the JD-Resume compatibility.'

        return  ret_val

