
from bs4 import BeautifulSoup
import os
import validators
import requests
from .pdfhtml import (
    pdf2htmlEX
)
import re
import pandas as pd
from typing import (
    List,
    Union,
    Iterable,
    Generator
)
import warnings

#customs
from .object_models import BxPath, BxCollection, BxInstruction
from . import exceptions


###
###
###quit()
###

HTML_FILE_ENCODING = 'latin-1' # often the cleanest for PDF HTMLs
DEFAULT_BS4_PARSER = 'html.parser'

DEFAULT_REGEX = {
    #TODO: change this regex as it's shit
    'float':r'(?<!\S)(?=.)(0|([1-9](\d*|\d{0,2}(,\d{3})*)))?(\.\d*[1-9])?(?!\S)', #supports str with commas also
}

###
###
###
###


class BxSoup(BeautifulSoup):

    """
    Init parameters
    ----------------

    :src [str]: url, filepath (.HTML or .XML) or html string to initialise the soup

    Classmethods:
    ----------------
    :BxSoup.from_pdf(): Creates a BxSoup object by converting a PDF document to HTML using
            various engines
    
    """

    def __init__(self,src: str):
        # handle urls
        if validators.url(src):
            html = requests.get(src).text
        elif os.path.exists(src) and src[-4:].lower() in ['html','.xml']:
            with open(src,'rb') as f:
                html = f.read().decode(HTML_FILE_ENCODING)
        else:
            html = src
        
        super().__init__(html,DEFAULT_BS4_PARSER)
    

    def generate_bxpaths(
            self,
            field_name: str,
            result_regex:str = None
            ) -> Generator[BxPath,None,None]:
        """
        This method will create a generator that will 
        auto-generate an array of BxPath "address" objects for
        a given data attribute that is tagged in the document using the BxTagging tool

        Parameters
        --------------
        :field_name [str]: name of the field-name attribute of extraction tags for this 
                field to be detected by the parser
        :result_regex [str]: regular expression for the normalisation/formatting/filtering 
                of the data attribute that is extracted. If this is None, default regex will
                be used for special data types that require normalisation (such as decimals).


        Returns
        --------------
        Generator of BxPath objects (one for each extraction tag found). Returns empty list 
        if no extraction tags found for the given data attribute

        :rtype: generator
        """

        tags = self.find_all('bx_extraction_tag',{
            'class':'extraction-tag',
            'field-name':field_name
        })


        for tag in tags:
            path = []

            # check for extraction tags wrapped in other extraction tags 
            # and move up to the parent html element of all tags
            while tag.parent.name=='bx_extraction_tag':
                tag = tag.parent

            # set tag focus to the parent
            tag = tag.parent 

            # the bxpath generation algorithm works by assessing how many of the current tag's
            # siblings have the same tag name and finds any unique attributes that make this tag
            # unique. If that is not possible then it works out which index the current tag
            # belongs to and uses that a reference to locate the tag in the instructions. 
            # This information is saved as a dictionary and added to the path as an explicit instruction.
            # If there is only one instance of the tag then the index or attributes are not used.
            # Then the focus shifts to the parent tag and the process is repeated. This continues
            # until there is no more parent tag (reaching the top of the soup)
            while tag.parent:
                path_item = {'tagName':tag.name, 'attrs':tag.attrs}
                same_name_attr_siblings = [tag.parent.find_all(tag.name,path_item['attrs'])]

                if len(same_name_attr_siblings)==1:
                    path_item['useIndex'],path_item['useAttrs']=False,True
                else:
                    sibling_index=0
                    for sibling in same_name_attr_siblings:
                        if sibling==tag:
                            # we found our focus tag
                            break
                        sibling_index+=1
                    path_item['index']=sibling_index
                    path_item['useIndex'],path_item['useAttrs']=True,False
                path.append(BxInstruction(**path_item))
                
                #move up
                tag = tag.parent

            # reverse order to present in order they should be executed, not how they were created
            yield BxPath(instructions=path[::-1],regex=result_regex, dataType=tags[0]['data-type'])

    def compile_bxpath(
            self,
            bxpath: BxPath, 
            as_text: bool = True, 
            result_attrs: Iterable = None,

            ) -> Union[str,BeautifulSoup,dict]:
        """
        This method will take a supplied bxpath, execute it and return the data attribute

        Parameters
        --------------
        :bxpath [BxPath]: BxPath address object of the data attribute to extract.
        :as_text [bool]: Default=True. Return value as a string rather than a BeautifulSoup tag object. Value regex 
                provided as part of the BxPath will only be applied if this flag is set to True.
        :result_attrs [Iterable]: Default=None. Iterable containing specific tag attrs to return instead of the tag text


        Returns
        --------------

        :rtype: BeautifulSoup -> tag object (if as_text=False and result_attrs=None)
        :rtype: str -> extracted text from target tag. (if as_text=True)
        :rtype: dict -> Dict of tag attrs (if as_text=False and result_attrs!=None)
        """

        tag = self
        for bxins in bxpath.instructions:

            same_name_siblings = tag.find_all(bxins.tagName)

            if bxins.useIndex:
                try:
                    tag = same_name_siblings[bxins.index]
                except IndexError as e:
                    raise exceptions.BxCompilationError(
                    f'IndexError: {e}. Could not find tag index {bxins.index} for "{bxins.tagName}" tag'
                    f' within parent tag "{tag.name}". Number of "{bxins.tagName}"  tags found: '
                    f'{len(same_name_siblings)} out of a set of {set([t.name for t in tag.find_all()])}'
                )

            elif bxins.useAttrs:
                try:
                    tag = [t for t in same_name_siblings if t.attrs==bxins.attrs][0]
                except IndexError as e:
                    raise exceptions.BxCompilationError(
                    f'IndexError: {e}. Could not find tag "{bxins.tagName}" matching attrs {bxins.attrs}'
                    f' within parent tag "{tag.name}". Number of "{bxins.tagName}"  tags found: '
                    f'{len(same_name_siblings)} out of a set of {set([t.name for t in tag.find_all()])}'
                )

            else:
                raise exceptions.BxCompilationError(
                    'Invalid BxInstruction object provided. Not instructed to use either tag index or attrs.'
                    f' Instruction provided: {bxins.dict()}'
                )
    
        if as_text:
            #remove dodgy encoding errors in string - using ONLY ascii
            t_text = ''.join([i if ord(i) < 128 else '' for i in tag.text.strip()])

            reg_to_use = DEFAULT_REGEX[bxpath.dataType] if bxpath.dataType in DEFAULT_REGEX.keys() else bxpath.regex
            if reg_to_use:
                reg = re.compile(reg_to_use)
                extracted_text = reg.search(t_text)
                if extracted_text:
                    #reg pulled a value
                    extracted_text = extracted_text.group()
                    return extracted_text
                else:
                    warnings.warn((
                        f'WARNING: regex value: {bxpath.regex} failed to detect an extractable value. '
                        'Whole value detected in tag being returned in its place. If you would '
                        'prefer this to throw an error rather than a warning, please set bx.WARN_LEVEL '
                        'to 2. To suppress this warning set bx.WARN_LEVEL to 0.'
                    ),exceptions.BxExtractionWarning
                )

            return tag.text.strip()
        if result_attrs:
            try:
                return {attr:getattr(tag,attr) for attr in result_attrs}
            except TypeError as e:
                raise exceptions.BxExtractionError(
                    f'TypeError: {e}. Make sure result_attrs is a valid iterable'
                )
            except AttributeError as e:
                raise exceptions.BxExtractionError(
                    f'AttributeError: {e}. result_attrs has attributes that do not belong to this tag '
                    f'Available attributes for "{tag.name}": {tag.attrs}'
                )
        return tag

    def extract_data(self,bxcoll: BxCollection,as_df:bool = False, fail_on_error=True) -> Union[dict,pd.DataFrame]:
        """
        This method will take a supplied collection of bxpath rules, and execute them on the document
        returning all extractable data for those rules. 

        Parameters
        --------------
        :bxcoll [BxCollection]: BxCollection object of BxPath rules.
        :as_df [bool]: returns a pandas dataframe instead of a dictionary of extracted values.
        :fail_on_error [bool]: Default=True. If a BxExtractionError occurs, this flag will force the 
                whole extraction to raise an exception. If False, this will save the error text as the value and 
                proceed with extracting other values.

        Returns
        -------------- 

        :rtype: dict -> format:  {'field':[value1,value2...]}
        :rtype: DataFrame -> data returned as pandas dataframe
        """
        res = {}
        for field,bxpaths in bxcoll.rules.items():
            res[field] = []
            for bxpath in bxpaths:
                try:
                    data_value = self.compile_bxpath(bxpath)
                except exceptions.BxExtractionError as e:
                    if fail_on_error:
                        raise exceptions.BxExtractionError(e)
                    else:
                        data_value = e
                
                res[field].append(data_value)
        if as_df:
            return pd.DataFrame(res)

        return res

    def get_tables(self,first_row_as_header:bool=True) -> List[pd.DataFrame]:
        """
        This method will return all html tables found in the soup as pandas dataframes.
        This is useful in cases where data already lies tabularised in the HTML document

        Parameters
        --------------
        :first_row_as_header [bool]: Default=True. Interpret first row of table as column headers

        Returns
        -------------- 

        :rtype: List[DataFrame]
        """
        return pd.read_html(
            str(self),
            header=0 if first_row_as_header else None
        )

    def generate_bxcollection(self) -> BxCollection:
        """
        This method is a shortcut to create a BxCollection (a collection of BxPath rules) object 
        from all bx extraction tags that are found in the soup. This method should only be 
        used on a "tagged" document that requires no specific regex for any of the tag text to 
        extract per tag.

        Parameters
        --------------
        None

        Returns
        -------------- 

        :rtype: BxCollection
        """
        field_names = set([tag.name for tag in self.find_all('bx_extraction_tag')])

        res = {}
        for field in field_names:
            res[field] = [p for p in self.generate_bxpaths(field)]
        return BxCollection(rules=res)


    @classmethod
    def from_pdf(cls,filepath: str, engine:str='pdf2htmlEX'):
        if engine=='pdf2htmlEX':
            dest = '\\'.join(filepath.split('\\')[:-1])
            html_file = pdf2htmlEX(filepath,dest)
        else:
            raise exceptions.BxCompilationError(f'PDF conversion engine {engine} not supported')

        return cls(src=html_file)





    







