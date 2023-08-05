#------------------------------------------------------------------------------
# Libraries
#------------------------------------------------------------------------------
# Standard
import os
import pandas as pd
import numpy as np
import bodyguard as bg

# Using SentenceTransformers NLP library
from sentence_transformers import SentenceTransformer

# Using HuggingFace NLP library
from transformers import AutoTokenizer, AutoModel
import torch
#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
class DocumentEmbedder(object):
    """
    Embedding of documents
    
    We rely on two major libraries to embed documents, namely https://github.com/UKPLab/sentence-transformers and https://huggingface.co/transformers/
    """
    # -------------------------------------------------------------------------
    # Constructor function
    # -------------------------------------------------------------------------
    def __init__(self,
                 normalize=True,
                 verbose=True,
                 model_name_or_path="all-roberta-large-v1",
                 ):
        self.normalize = normalize
        self.verbose = verbose
        self.model_name_or_path = model_name_or_path
        
    # -------------------------------------------------------------------------
    # Class variables
    # -------------------------------------------------------------------------
    MAX_SQN_LENGTH = 256
    RETURN_TYPE_OPT = ["dict", "df"]
    STR_USING_SAVED_MODEL = "Using saved model: '{0}'"
    STR_DOWNLOADING_MODEL = "Downloading model: '{0}'"    
    STR_DOCUMENTS_NEED_EMBEDDING_INPUT = "Embeddings from model '{0}' needed"

    # -------------------------------------------------------------------------
    # Private functions
    # -------------------------------------------------------------------------    
    #Mean Pooling - Take attention mask into account for correct averaging
    def _mean_pooling(self, model_output, attention_mask):
        """
        See example here: https://huggingface.co/sentence-transformers/all-roberta-large-v1
        """
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        mean_embeddings = sum_embeddings / sum_mask
    
        return mean_embeddings

    def _check_embeddings_existence(self, documents, model_name_or_path):
        """Check which documents that need to be embeddings versus which documents that have already been embedded"""
        
        # Check if embeddings exist using this particular method
        if hasattr(self, model_name_or_path+"-embeddings"):
            if self.verbose:
                print(f"Embeddings from model '{model_name_or_path}' found")
            # Load existing embeddings
            documents_embeddings = getattr(self, model_name_or_path+"-embeddings")
            
            # Check which documents have not already been embedded
            documents_not_embedded = []
            for doc in documents:
                if documents_embeddings.get(doc) is None:
                    documents_not_embedded.append(doc)                
        else:
            setattr(self, model_name_or_path+"-embeddings", {})
            documents_not_embedded = documents
        
        return documents_not_embedded

    
    def _extract_existing_embeddings(self, documents, model_name_or_path):
        """Extract those embeddings that have already been embedded"""
        # Extract relevant document embeddings
        embeddings = {k:getattr(self, model_name_or_path+"-embeddings")[k] for k in documents}
        
        return embeddings

    def _extract_embedding_by_str(self, embeddings, which_embedding):
        """
        Extract specific embeddings by str (key in dict of embeddings)
        """
        # Sanity check inputs
        bg.sanity_check.check_type(x=embeddings,
                                   allowed=dict,
                                   name="embeddings")

        bg.sanity_check.check_type(x=which_embedding,
                                   allowed=str,
                                   name="which_embedding")
    
        # Looking for a specific embedding
        if which_embedding in embeddings:
            embeddings = embeddings[which_embedding]
        else:
            raise Exception(f"Embedding '{which_embedding}' not found in existing embeddings, which include: \n{list(embeddings.keys())}. \nPlease embed!")
        
        return embeddings

    def _embed_documents(self,
                         documents,
                         model_name_or_path="all-roberta-large-v1"):
                
        # ---------------------------------------------------------------------
        # Check documents have been embedded before
        # ---------------------------------------------------------------------
        documents_not_embedded = self._check_embeddings_existence(documents=documents,
                                                                  model_name_or_path=model_name_or_path)

        if bool(documents_not_embedded):
            # We have assessed that some documents have not been embedded, hence we construct embeddings and save them!
            if self.verbose:
                print(self.STR_DOCUMENTS_NEED_EMBEDDING_INPUT.format(model_name_or_path))
                
            # -----------------------------------------------------------------
            # Check if model is already loaded
            # -----------------------------------------------------------------
            if hasattr(self, model_name_or_path+"-model"):
                if self.verbose:
                    print(self.STR_USING_SAVED_MODEL.format(model_name_or_path))
                    
                pretrained_model = getattr(self, model_name_or_path+"-model")
                tokenizer = getattr(self, model_name_or_path+"-tokenizer")
                
            else:
                if self.verbose:
                    print(self.STR_DOWNLOADING_MODEL.format(model_name_or_path))
    
                try:
                    # Load model via SentenceTransformer
                    pretrained_model = SentenceTransformer(model_name_or_path=model_name_or_path)
                    tokenizer = None
                    self.loaded_via = "SentenceTransformer"
                except:                
                    try:
                        # Load model via HuggingFace
                        pretrained_model = AutoModel.from_pretrained(model_name_or_path)
                        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
                        self.loaded_via = "HuggingFace"
                    except OSError as err:
                        raise Exception(f"Could not load '{model_name_or_path}'. \nWhile trying, this error occured: \n\n{err}")
                        
                # Set tokenizer and pretrained model as attributes under the model name.
                setattr(self, model_name_or_path+"-model", pretrained_model)
                setattr(self, model_name_or_path+"-tokenizer", tokenizer)        
                
            # -----------------------------------------------------------------
            # Embed
            # -----------------------------------------------------------------            
            if self.loaded_via=="SentenceTransformer":
                            
                # Update maximum sequence length
                pretrained_model.max_seq_length = self.MAX_SQN_LENGTH
    
                # Construct embedding
                raw_embeddings = pretrained_model.encode(documents_not_embedded,
                                                         batch_size=32,
                                                         show_progress_bar=False,
                                                         output_value="sentence_embedding",
                                                         convert_to_numpy=True,
                                                         convert_to_tensor=False,
                                                         device=None,
                                                         normalize_embeddings=True)
                            
            elif self.loaded_via=="HuggingFace":
    
                # Tokenize sentences
                encoded_input = tokenizer(text=documents_not_embedded,
                                          padding=True,
                                          truncation=True,
                                          max_length=self.MAX_SQN_LENGTH,
                                          return_tensors='pt')
            
                # Compute token embeddings
                with torch.no_grad():
                    model_output = pretrained_model(**encoded_input)
            
                # Perform pooling (here, mean pooling)
                raw_embeddings = self._mean_pooling(model_output=model_output,
                                                    attention_mask=encoded_input['attention_mask'])                
    
                # Convert tensor to numpy array
                raw_embeddings = raw_embeddings.numpy()
    
            # -----------------------------------------------------------------
            # Finalize
            # -----------------------------------------------------------------
            # Pre-allocate
            embeddings = {}
            
            for i,doc in enumerate(documents_not_embedded):
                embeddings[doc] = raw_embeddings[i,:].reshape(-1,)
                
            # Update existing document embeddings
            setattr(self, model_name_or_path+"-embeddings", {**getattr(self, model_name_or_path+"-embeddings"),
                                                             **embeddings}
                    )            
            
        # Extract embeddings
        embeddings_out = self._extract_existing_embeddings(documents=documents,
                                                           model_name_or_path=model_name_or_path)
        
        return embeddings_out
    # -------------------------------------------------------------------------
    # Public functions
    # -------------------------------------------------------------------------
    def show_available_models(self):
        """Print available models via SentenceTransformers"""
        
        # Last last updated
        DATE_LAST_UPDATED = "February 3, 2022"
        
        # Models
        AVAILABLE_MODELS_VIA_SENTENCETRANSFORMERS = ["all-roberta-large-v1",
                                                     "all-mpnet-base-v1",
                                                     "all-mpnet-base-v2"
                                                     "all-MiniLM-L12-v1",
                                                     "all-distilroberta-v1",
                                                     "all-MiniLM-L12-v2",
                                                     "all-MiniLM-L6-v2",
                                                     "all-MiniLM-L6-v1",
                                                     "paraphrase-mpnet-base-v2",
                                                     "multi-qa-mpnet-base-dot-v1",
                                                     "multi-qa-distilbert-dot-v1",
                                                     "multi-qa-mpnet-base-cos-v1",
                                                     "paraphrase-distilroberta-base-v2",
                                                     "paraphrase-TinyBERT-L6-v2",
                                                     "paraphrase-MiniLM-L12-v2",
                                                     "multi-qa-distilbert-cos-v1",
                                                     "paraphrase-multilingual-mpnet-base-v2",
                                                     "paraphrase-MiniLM-L6-v2",
                                                     "paraphrase-albert-small-v2",
                                                     "multi-qa-MiniLM-L6-cos-v1",
                                                     "paraphrase-multilingual-MiniLM-L12-v2",
                                                     "multi-qa-MiniLM-L6-dot-v1",
                                                     "msmarco-bert-base-dot-v5",
                                                     "msmarco-distilbert-base-tas-b",
                                                     "paraphrase-MiniLM-L3-v2",
                                                     "msmarco-distilbert-dot-v5",
                                                     "distiluse-base-multilingual-cased-v1",
                                                     "distiluse-base-multilingual-cased-v2",
                                                     "average_word_embeddings_komninos",
                                                     "average_word_embeddings_glove.6B.300d",
                                                     ]
        
        bg.tools.print2(f"""As of out {DATE_LAST_UPDATED}, these models are available through SentenceTransformers: \n\n {AVAILABLE_MODELS_VIA_SENTENCETRANSFORMERS}""")

    def embed_documents(self,
                        documents,
                        return_embeddings=True,
                        return_type="df"): 
        """
        Embed documents as vectors
        """
        # Check types
        bg.sanity_check.check_type(x=documents,
                                   allowed=(list,str),
                                   name="documents")
        
        # Convert to list if str
        if isinstance(documents, str):
            documents = [documents]
        
        # Check inputs
        bg.sanity_check.check_str(x=return_type,
                                  allowed=self.RETURN_TYPE_OPT,
                                  name="return_type")
                        
        # Embed documents
        embeddings = self._embed_documents(documents=documents,
                                           model_name_or_path=self.model_name_or_path)
                    
        # Normalize
        if self.normalize:
            if isinstance(embeddings, dict):             
                embeddings = {k: bg.distance.normalize_by_norm(x=v,norm="L2") for k,v in embeddings.items()}
                
        # Convert to df to change column type              
        embeddings = bg.convert.convert_dict_to_df(x=embeddings)
        
        # Enforce columns to be strings
        embeddings.columns = embeddings.columns.astype(str)
                
        if return_type=="dict":
            embeddings = bg.convert.convert_df_to_dict(x=embeddings)    
        
        if return_embeddings:
            return embeddings
    
    def extract_embeddings(self,embeddings=None,which_embeddings="all",return_type="df"):
        
        if embeddings is None:
            # Extract all existing embeddings
            embeddings = getattr(self, self.model_name_or_path+"-embeddings")

        bg.sanity_check.check_type(x=embeddings,
                                   allowed=dict,
                                   name="embeddings")
        
        bg.sanity_check.check_type(x=which_embeddings,
                                   allowed=(str,list),
                                   name="which_embeddings")

        if which_embeddings=="all":
            # Return all embeddings
            pass
        elif isinstance(which_embeddings, str):
            
            embeddings = {which_embeddings: self._extract_embedding_by_str(embeddings=embeddings,
                                                                           which_embedding=which_embeddings)
                          }
            
        elif isinstance(which_embeddings, list):
            
            # Pre-allocate
            embeddings_temp = {}

            # Exact all individual embeddings
            for s in which_embeddings:                
                embeddings_temp[s] = self._extract_embedding_by_str(embeddings=embeddings,
                                                                    which_embedding=s)  
                
            # Overwrite
            embeddings = embeddings_temp
                                
        if return_type=="df":
            embeddings = bg.convert.convert_dict_to_df(x=embeddings)
            
        return embeddings
            
    def compute_similarity_between_two_embeddings(self,a,b,metric="Lknorm",**kwargs):

        # Sanity check
        bg.sanity_check.check_type(x=a, allowed=str, name="a")
        bg.sanity_check.check_type(x=b, allowed=str, name="b")
        
        # Join as list
        ab = [a,b]
        
        # Get embeddings
        embeddings = self.embed_documents(documents=ab,
                                          return_embeddings=True,
                                          return_type="df")

        # Compute similarity
        similarity = bg.distance.compute_similarity(a=embeddings.loc[a],
                                                    b=embeddings.loc[b],
                                                    metric=metric,
                                                    **kwargs)
        
        # Extract
        similarity = similarity.iloc[0,0]
        
        return similarity
                
    def compute_similarity(self,a,b,metric="Lknorm",**kwargs):

        # Sanity check
        bg.sanity_check.check_type(x=a, allowed=(str,list), name="a")
        bg.sanity_check.check_type(x=b, allowed=(str,list), name="b")
        
        # Convert to list if str
        if isinstance(a,str):
            a = [a]
        if isinstance(b,str):
            b = [b]        
        
        # Join as list
        ab = a+b
        
        # Get embeddings
        embeddings = self.embed_documents(documents=ab,
                                          return_embeddings=True,
                                          return_type="dict")
        
        a_embeddings = self.extract_embeddings(embeddings=embeddings,
                                               which_embeddings=a,
                                               return_type="df")

        b_embeddings = self.extract_embeddings(embeddings=embeddings,
                                               which_embeddings=b,
                                               return_type="df")        

        # Compute similarity
        similarity = bg.distance.compute_similarity(a=a_embeddings,
                                                    b=b_embeddings,
                                                    metric=metric,
                                                    **kwargs)
        
        
        
        return similarity
