# Bx

### Add-on to the great BeautifulSoup library for rules-generation and compilation for the purpose of automated rules-based information extraction from HTML-converted documents.

&nbsp;

# Background

Dynamically extracting information from PDF and other similar types of documents can be very chellenging owing to the fact that these documents are digital, but were designed for human consumption and use, often employing legal and natural language and unpredictable formatting.

Although extracting text from PDFs is well-trodden ground, much non-linguistic information such as table boundaries, lists and sections are lost, making the information extraction task more difficult. Currently, only a handful of solid frameworks exist that preserve the format of a PDF document when converting to a more editable format and even fewer that combine this a conversion framework and one for information extraction.

**Bx** aims to solve this by combining the use of different PDF conversion engines with the powerful BeautifulSoup web-scraping library to present a framework for automating the processing of human-targeted documents in the fastest possible way.

Key features include:
* User interface for "tagging" HTML-converted documents. This is for "training" the system. This involves a user simply highlighting the data they want on a document and the Bx UI will inject an HTML tag to wrap the data required for the back end rule generation.
* Automated rule generation. Once documents are "tagged", Bx can generate a set of rules from the user-demarcated tags
* Rule compilation: Bx also has methods to execute an extraction process based on the outputted collection of rules

### Example usage:
Setting up an entire Bx workflow can be simple. Below is an example of what is required to turn 100 PDF documents into 1 large pandas dataframe with each row being extracted data from a document, after the first one is tagged in the UI.
```python
from bx.soup import BxSoup

path_html_of_tagged_pdf = '/path/to/file.html'

# train Bx for a particular type of document

train_soup = BxSoup(path_html_of_tagged_pdf)
document_rules_collection = S.generate_bxcollection()

#extract data from our bank of untagged raw PDFs
documents_data = []
for pdf in list_of_pdf_file_paths:
    exe_soup = BxSoup.from_pdf(pdf,engine='pdf2htmlEX')
    result_df = exe_soup.extract_data(document_rules_collection,as_df=True)
    documents_data.append(result_df)

#put together
final_df = pd.concat(documents_data)
```

***NB***. It's important to note in this example that Bx is not dependent on a data attribute being present in a table for rules generation to work. A value can be present anywhere in the document for Bx to be able to generate a rule for extraction.

&nbsp;

# Key features and Components

The primary BxSoup class is a thin extension of the BeautifulSoup class to include specfic methods for information extraction. This section details other key objects as part of this implementation.

## BxPath
One of the main benefits of Bx is the capability to use user-demarcated data attributes and return a unique "address" for the location of that data attribute within the document. This is known as the *BxPath* of a data attribute and works in a similar way to the established XPATH querying language used to "locate" elements in an XML tree, but with several key differences:

### 1. No XPATH querying in BeautifulSoup

BeautifulSoup does not natively support XPATH, therefore providing an "address" for an unknown but expected element would require some kind of query mechanism. A BxPath is created by powerful BeautifulSoup methods and can be handled and used with very little or no custom code required.

### 2. XPATHs can be challenging to maintain

Another advantage that BxPaths enjoy over XPATHs is that they can be less-sensitive to slight variations in the HTML tree. Not every instance of the same PDF format will be converted or presented in the same way, so the BxPath generator also looks for attributes that uniquely identify an element without having to copy the whole path, making it less sensitive to slight variations in format. 

### 3. JSON-formatted
BxPaths, although technically a pydantic object, are easily translated into JSON format, which means they are highly scalable and customisable, the intention here being to make Bx highly adaptable to future changes

### 4. Regex support
Unlike XPATH, BxPath can handle regular expressions, meaning that the text found within the target parent element of the data we are searching for can be filtered to just the data that we want. For example, say we are looking for the ticker of the company in our PDF document and the data we want is contained in the following "p" tag:
```html
<p>
    Informa (LSE: INF.L), the Information Services, Advanced Learning, B2B Exhibitions and Events Group today held its General Meeting at 5 Howick Place, London, SW1P 1WG. All resolutions put to the General Meeting were voted on by way of a poll and were approved by Shareholders. 
</p>
```
> Source: LSE website

By using a regular expression in the BxPath we can instruct the extractor to only take the portion of text that we want (in this case: "INF.L"). If we extract the whole document as a row in a dataframe, then we would expect just the value of the ticker under the "ticker" column.

&nbsp;

## BxSoup class

BxSoup extends the BeautifulSoup class by providing methods that enable automated rules-generation and compilation for multiple data attributes or a given document. Here are the key features and functionality of this class:

### 1. Low-code BxPath generation
Very little custom code needs to be written by a developer to translate a user-tag into a unique BxPath.

### 2. User-friendly interface
As any data scientist will attest to, getting hold of data from non-technical or business side stakeholders can be a challenging to and fro of confusing spreadsheets and emails. Bx seeks to eliminate this by providing a UI that users can leverage to highlight the data that is required in the document. The resultant HTML document is all Bx needs to automate the rest of rules generation. Of course, custom regex can also be applied at this stage.

&nbsp;


## PDF --> HTML Conversion
Bx also leverages the powerful command line utility *pdf2htmlEX* to convert PDF documents to HTML. 

Bx also includes a python interface to Microsoft Word (which as it happens has a very decent PDF conversion capability) through *pywin32* to dynamically convert any document that can be opened natively in Word to HTML.

&nbsp;

&nbsp;


# TODO:
A list of expansion ideas an future functionality for Bx

- [x] Add Ms Word backend



