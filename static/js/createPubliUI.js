async function createPubliUI(publi,toolTips=false,abstract=false) {
  const art = $("<article/>").addClass("publi")
  art.className = "publi"
  $("<a/>", {
    href: publi.URL,
    target: "_blank"
  }).html($("<h1/>").text(publi.title[0])).appendTo(art)
  const authors = publi.author
  const ulauthors = $("<ul/>").addClass("authors-list").appendTo(art)
  for (const author of authors) {
    const liauth = $("<li/>").addClass("author-item")
    const spanAuth = $("<span/>").text(String.raw`${author.given} ${author.family}`).appendTo(liauth)
    var notifycontent = $("<div/>").addClass("author-info")
    $("<h1/>").text(String.raw`${author.given} ${author.family}`).appendTo(notifycontent)
    ulaff = $("<ul/>").addClass("affiliation-list").appendTo(notifycontent)
    if (author.affiliation) {
      for (const a of author.affiliation) {
        $("<li/>").text(a.name).appendTo(ulaff)
      }
    }
    if (author["authenticated-orcid"]) {
      const html = String.raw`<div class="orcid-id"><a href="https://orcid.org" target="_blank"><img alt="ORCID logo" src="https://orcid.org/sites/default/files/images/orcid_16x16.png" width="16" height="16"/></a> <a href="${author.ORCID}" target="_blank">${author.ORCID} </a></div>`
      notifycontent.append(html)
    }
    if (toolTips) {
      tippy(spanAuth[0], {
        content: notifycontent[0],
        theme: 'light',
        interactive: true,
      });  
    }
    
    ulauthors.append(liauth)
  }
  journaldiv = $("<div/>").appendTo(art)
  if ("container-title-short" in publi && publi["container-title-short"].length>0) {
    var title_short = $("<span/>").text(publi["container-title-short"][0])
    journaldiv.append(title_short)
    if (toolTips) {
      tippy(title_short[0], {
        content: publi["container-title"][0],
        theme: 'light',
      });
    }
  }
  else {
    $("<span/>").text(publi["container-title"][0]).appendTo(journaldiv)
  }
  var publiDate = pubUtils.bestDate(publi)
  var date = pubUtils.parseDate(publiDate.dateInfo)
  journaldiv.append(" ")
  $("<span/>").text(date.getFullYear().toString()).appendTo(journaldiv)
  journaldiv.append(" ")
  $("<span/>").text(publi.volume).appendTo(journaldiv)
  if (publi.issue) {
    $("<span/>").addClass("issue").text(publi.issue).appendTo(journaldiv)
    journaldiv.append(", ")
    $("<span/>").text(publi.page).appendTo(journaldiv)
  }
  $("<a/>", {
    href: publi.URL,
    target: "_blank"
  }).text(String.raw`DOI: ${publi.DOI}`).appendTo(art)

  $("<p/>").append(`${publiDate.type== "created" ? "First p" : "P"}ublished on `).append($("<time/>", {
    datetime: date.toISOString().substring(0, 10)
  }).text(date.toLocaleDateString("en-us", {
    day: "numeric",
    month: "short",
    year: "numeric"
  }))).appendTo(art)
  if (abstract) {
   var ab = $("<section>",{id: "abstract",}).addClass("well").addClass("abstract")
   var abfig =$("<figure>").addClass("picture")
   abfig.appendTo(ab)
   $("<img>",{src:publi.PictureURL}).appendTo(abfig)
   var htmltxt = await publi.getAbstractTextAsync()
   abtxt=$("<p>").html(htmltxt)
   abtxt.appendTo(ab)
   art.append(ab)
  }
  return art
}