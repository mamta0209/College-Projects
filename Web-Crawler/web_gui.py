import Tkinter
from Tkinter import *
import tkMessageBox
import webbrowser
import tkHyperlinkManager


def get_page(url):
    try:
        import urllib
        return urllib.urlopen(url).read()
    except:
        return ""

# Help function that return first link and end position of the link
def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote

# Help function union two arrays
def union(p,q):
    for e in q:
        if e not in p:
            p.append(e)

# Function that extracts all links from requested page
def get_all_links(page):
    links = []
    while True:
        url,endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links

# Initial function that starts the web crawling on a particular URL
#def crawl_web(seed, max_depth):
def crawl_web(seed):
    tocrawl = [seed]
    crawled = []
    index = {}
    graph = {}
    next_depth = []
    depth = 0
    #while tocrawl and depth <= max_depth:
    while tocrawl:
        page = tocrawl.pop()
        if page not in crawled:
            content = get_page(page)
            add_page_to_index(index,page,content)
            outlinks = get_all_links(content)
            graph[page] = outlinks
            union(tocrawl, outlinks)
            #union(next_depth, outlinks)
            crawled.append(page)
        #if not tocrawl:
			#tocrawl, next_depth = next_depth, []
			#depth += 1
    return index, graph

#
# Functions required for indexing, crawled pages
#

# Function that add word to the index
def add_to_index(index,keyword,url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]

# search the index for the keyword
def lookup(index,keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None

# Function that splits page into words and adds them to index
def add_page_to_index(index,url,content):
    words = content.split()      #can be improved upon
    for keyword in words:
        add_to_index(index,keyword,url)

# Function for recording cliks on a particular link
def record_user_click(index,keyword,url):
    urls = lookup(index, keyword)
    if urls:
        for entry in urls:
            if entry[0] == url:
                entry[1] += 1

#
# Functions required for ranking
#

# Function that computes page ranks
#
# Formula to count rank:
#
# rank(page, 0) = 1/npages
# rank(page, t) = (1-d)/npages
#                 + sum (d * rank(p, t - 1) / number of outlinks from p)
#                 over all pages p that link to this page
#
def compute_ranks(graph):
    d = 0.8 #dumping constant
    numloops = 40

    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages

    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            #Loop throught all pages
            for node in graph:
                #check if node links to page
                if page in graph[node]:
                    #Add to new rank based on this node
                    newrank += d * ranks[node] / len(graph[node])
            newranks[page] = newrank
        ranks = newranks
    return ranks

# Function that returns the one URL most likely to be the best site for that
# keyword. If the keyword does not appear in the index return None
def lucky_search(index, ranks, keyword):
    return_url = '';
    if keyword not in index:
        return None
    for url in index[keyword]:
        if url in ranks:
            if return_url != '':
                if ranks[url] > ranks[return_url]:
                    return_url = url
            else:
                return_url = url
    return return_url

# Function that returns the list of all URLs for that keyword. Ordered by page
# rank. If the keyword does not appear in the index return None
def ordered_search(index, ranks, keyword):
    pages = lookup(index, keyword)
    return quick_sort(pages, ranks)

# Help function that uses quick sort algorithm to order array
def quick_sort(pages, ranks):
    if not pages or len(pages) <= 1:
        return pages
    else:
        pivot = ranks[pages[0]] #find pivot
        worse = []
        better = []
        for page in pages[1:]:
            if ranks[page] <= pivot:
                worse.append(page)
            else:
                better.append(page)
    return quick_sort(better, ranks) + [pages[0]] + quick_sort(worse, ranks)


#index, graph = crawl_web('https://en.wikipedia.org/');
#index, graph = crawl_web('http://www.udacity.com/cs101x/urank/index.html');
#print "\n Index: \n"
#print index
#print "\n Graph: \n"
#print graph

#ranks = compute_ranks(graph)
#print ranks

#print ordered_search(index, ranks, 'Hindi')
##print ordered_search(index, ranks, 'Hummus')

root = Tk()
root.title("Crawler")
root.attributes('-zoomed',True)
root.configure(bg='gray')

root.resizable(4,4)
yscrollbar = Scrollbar(root)
yscrollbar.pack(side=RIGHT, fill=Y)
text = Text(root,background = 'gray',foreground='black',font = ('Arial',15),
            yscrollcommand=yscrollbar.set)
hyperlink=tkHyperlinkManager.HyperlinkManager(text)
yscrollbar.config(command=text.yview)
text.grid_forget()

L1 = Label(root,background = 'gray',foreground='white',font = ('Arial',20,'bold'),bd=5,text="Mini-Crawler")

L1.pack( side = LEFT)
L1.place(x=15,y=15)


E1 = Entry(root,width=50,font = ('Arial',20),bd=5)
E1.pack(side = LEFT)
E1.place(x=200,y=15)
E1.grid_forget()

def OpenUrl(url):
	webbrowser.open_new(url)

def click1():
	print "clicked"

def callback():
	print E1.get()
	str_input = E1.get()
	#index , graph = crawl_web('http://www.bikatadventures.com/Home/Blog/Travel-options-for-the-base-point-of-Goecha-La-trek-Yuksom',1)
	index, graph = crawl_web('http://www.udacity.com/cs101x/urank/index.html');
	ranks = compute_ranks(graph)
	list1= ordered_search(index, ranks, str_input)
	text.delete('1.0',END)
	for w in list1:
		text.insert(INSERT, w,hyperlink.add(click1))
		text.insert(INSERT,"\n\n")
		text.pack()

	text.place(x=50,y=100)
	root.mainloop()

B = Tkinter.Button(root, background = 'grey',foreground='white',text ="Search",font=('Arial', 20, 'bold', 'italic'), command = callback)

B.pack()
B.place(x=1000,y=15)


root.mainloop()
