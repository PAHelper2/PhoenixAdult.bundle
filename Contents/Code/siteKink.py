import PAsearchSites
import PAgenres

def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate, searchAll, searchsiteID):
    searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle)
    for searchResult in searchResults.xpath('//div[contains(@class,"shoot")]'):
        titleNoFormatting = searchResult.xpath('.//div[@class="shoot-thumb-title"]/div[@class="script"]/a/text()')
        Log(str(titleNoFormatting))

        # href of shoot is first a href
        curID = searchResult.xpath('.//a[1]/@href')
        curID = curID.replace('/','_')
        Log("ID: " + curID)

        releasedDate = searchResult.xpath('.//div[@class="date"]/text()')
        releasedDate = datetime.strptime(releasedDate, '%b %d, %Y').strftime('%Y-%m-%d')
        Log(str(releasedDate))

        lowerResultTitle = str(titleNoFormatting).lower()
        if searchByDateActor != True:
            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
        else:
            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%Y-%m-%d')
            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
        titleNoFormatting = titleNoFormatting + " [" + PAsearchSites.searchSites[siteNum][1] + ", " + releasedDate + "]"
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
    return results

def update(metadata,siteID,movieGenres):
    Log('******UPDATE CALLED*******')
    temp = str(metadata.id).split("|")[0].replace('_','/')

    url = PAsearchSites.getSearchBaseURL(siteID) + temp
    detailsPageElements = HTML.ElementFromURL(url)

    # Summary
    metadata.studio = "Kink.com"
    metadata.summary = detailsPageElements.xpath('//meta[@name="description"]/@content')
    metadata.title = detailsPageElements.xpath('//title/text()')
    releasedDate = detailsPageElements.xpath('//div[@class="updatedDate"]')[0].text_content()[14:24]
    date_object = datetime.strptime(releasedDate, '%Y-%m-%d')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # <div class="shoot-page" data-shootid="42767" data-sitename="sexandsubmission" data-director="[object Object]">
    # d.xpath('//link[@rel="shortcut icon"]/@href')
    metadata.tagline = detailsPageElements.xpath('//div[@class="shoot-page"]/@data-sitename')
    metadata.collections.clear()
    metadata.collections.add(metadata.tagline)


    # Genres
    # movieGenres.clearGenres()
    # genres = detailsPageElements.xpath('//div[contains(@class,"sceneColCategories")]//a')
    #
    # if len(genres) > 0:
    #     for genreLink in genres:
    #         genreName = genreLink.text_content().strip('\n').lower()
    #         movieGenres.addGenre(genreName)

    # Actors
    metadata.roles.clear()
    actors = detailsPageElements.xpath('//span[@class="names"]/a')
    if len(actors) > 0:
        for actorLink in actors:
            role = metadata.roles.new()
            actorName = actorLink.text_content()
            role.name = actorName
            actorPageURL = actorLink.get("href")
            actorPage = HTML.ElementFromURL(PAsearchSites.getSearchBaseURL(siteID) + actorPageURL)
            # actorPhotoURL = actorPage.xpath('//img[@class="actorPicture"]')[0].get("src")
            # role.photo = actorPhotoURL

    # Posters/Background
    valid_names = list()
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_names)

    # <video id="kink-player" class="video-js vjs-fluid video-player" width="100%" height="100%" poster="https://cdnp.kink.com/imagedb/42767/i/h/830/18.jpg"></video>
    # <span data-type="trailer-src" data-url="https://cdnp.kink.com/imagedb/42767/v/h/new/42767_7_480p.mp4"></span>
    posterURL = detailsPageElements.xpath('//video[@poster]/@poster')
    Log("Kink Poster URL: " + posterURL)
    metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL).content, sort_order = 1)

    background = detailsPageElements.xpath('//video[@poster]/@poster')
    metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
    metadata.posters[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
    return metadata
