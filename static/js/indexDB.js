class indexDB {
  static async loadAsync() {
    if (window.indexDB) {
      return window.indexDB
    }
    var db = new indexDB
    const maxAge= (DebugMode.Enabled,0,600)
    var site_url = "/"+window.location.pathname.split('/')[1];
    const text = await getTextFromFileUrlAsync(site_url+"/data/index.yaml",{"Cache-Control":`max-age=${maxAge}`})
    const myYaml = jsyaml.load(text);
    db.sets = ((myYaml.sets === undefined) ? new Map() : new Map(Object.entries(myYaml.sets)));
    db.others = ((myYaml.others === undefined) ? [] : Array.from(myYaml.others));
    db.reviews = ((myYaml.reviews === undefined) ? [] : Array.from(myYaml.reviews));
    window.indexDB=db
    return db
  }
}
