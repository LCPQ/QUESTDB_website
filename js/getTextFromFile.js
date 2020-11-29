var fileCache = function () {
  var site_url = "/"+window.location.pathname.split('/')[1];
  var json_url = site_url+"/data/database.json";
  var req = new XMLHttpRequest();
  req.open("GET",json_url, false);
  req.send();
  return JSON.parse(req.responseText);
}


_cache = fileCache();
function getTextFromFileUrl(url,header={}) {
  if (url in _cache) {
    return _cache[url];
  } else {
    return async () => {await getTextFromFileUrlAsync(url)};
  }
}


async function getTextFromFileUrlAsync(url,header={}) {
  return new Promise(function (resolve, reject) {
  var req = new XMLHttpRequest();
  req.open("GET",url, true);
  for (const [key, val] of Object.entries(header)) {
    req.setRequestHeader(key,val)
  }
  req.onreadystatechange = function() {
    if (req.readyState == 4) {
      if (req.status == 200 || req.status==304) {//when a good response is given do this
        var text = req.responseText;
        resolve(text);
      } else {
        reject({
          status: req.status,
          statusText: req.statusText
        });
      }
    }
  }
  req.send();
  });
}
async function getTextFromUploadedFileAsync(inputFile){
  const temporaryFileReader = new FileReader();

  return new Promise((resolve, reject) => {
    temporaryFileReader.onerror = () => {
      temporaryFileReader.abort();
      reject(new DOMException("Problem parsing input file."));
    };

    temporaryFileReader.onload = () => {
      resolve(temporaryFileReader.result);
    };
    temporaryFileReader.readAsText(inputFile);
  });
};
