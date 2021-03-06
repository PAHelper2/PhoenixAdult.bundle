import PAsearchSites
import PAgenres
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchAll,searchSiteID):
    searchPageContent = HTTP.Request("https://www.pornfidelity.com/episodes/?search=" + encodedTitle)
    searchPageContent = str(searchPageContent).split('":"')
    searchPageResult = searchPageContent[len(searchPageContent)-1][:-2]
    searchPageResult = searchPageResult.replace('\\n',"").replace('\\',"")
    Log(searchPageResult)
    searchResults = HTML.ElementFromString(searchPageResult)
    for searchResult in searchResults.xpath('//div[contains(@class,"episode")]'):
        titleNoFormatting = searchResult.xpath('.//div[@class="card-title"]')[0].text_content()
        Log(titleNoFormatting)
        curID = searchResult.xpath('.//a[contains(@class,"card-link")]')[0].get('href')
        curID = curID.replace('/','_')
        curID = curID[8:-19]
        Log("ID: " + curID)
        releasedDate = searchResult.xpath('.//div[contains(@class,"card-meta")]//div[contains(@class,"text-left")]')[0].text_content()[19:-4]
        if ", 20" not in releasedDate:
            releasedDate = releasedDate + ", " + str(datetime.now().year)
        Log(str(curID))
        lowerResultTitle = str(titleNoFormatting).lower()
        if searchByDateActor != True:
            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
        else:
            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%b %m, $Y')
            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
        titleNoFormatting = titleNoFormatting + " [" + PAsearchSites.searchSites[siteNum][1] + ", " + releasedDate + "]"
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))




    return results



def update(metadata,siteID,movieGenres):
    Log('******UPDATE CALLED*******')
    temp = str(metadata.id).split("|")[0].replace('_','/')

    url = "https://" + temp
    detailsPageElements = HTML.ElementFromURL(url)

    # Summary
    metadata.studio = "Kelly Madison"
    metadata.summary = detailsPageElements.xpath('//p[contains(@class,"card-text")]')[0].text_content()
    metadata.title = detailsPageElements.xpath('//h4')[0].text_content()[36:]
    Log(metadata.title)
    metadataParts = detailsPageElements.xpath('//div[contains(@class,"episode-summary")]//h4')
    for metadataPart in metadataParts:
        if "Published" in metadataPart.text_content():
            releasedDate = metadataPart.text_content()[39:49]
            Log(releasedDate)
            date_object = datetime.strptime(releasedDate, '%Y-%m-%d')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year 
    
    

    # Genres
    movieGenres.clearGenres()
    movieGenres.addGenre("Hardcore")
    movieGenres.addGenre("Heterosexual")

    # Actors
    metadata.roles.clear()
    actors = detailsPageElements.xpath('//div[contains(@class,"episode-summary")]//a[contains(@href,"/models/")]')
    if len(actors) > 0:
        for actorLink in actors:
            role = metadata.roles.new()
            actorName = actorLink.text_content()
            role.name = actorName
            actorPageURL = actorLink.get("href")
            actorPage = HTML.ElementFromURL(actorPageURL)
            actorPhotoURL = actorPage.xpath('//img[@class="img-fluid"]')[0].get("src")
            role.photo = actorPhotoURL

    # Posters/Background
    valid_names = list()
    pageSource = str(HTTP.Request(url))
    posterStartPos = pageSource.index('poster: "')
    posterEndPos = pageSource.index('"',posterStartPos+10)
    background = pageSource[posterStartPos+9:posterEndPos]
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_names)
    try:
        metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
    except:
        pass
    try:
        metadata.posters[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
    except:
        pass
    


    
    return metadata
