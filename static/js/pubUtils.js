class pubUtils {
  static parseDate(date) {
    if (date["date-time"]) {
      return Date.parse(date["date-time"])
    }
    if (date.timestamp) {
      return Date(date.timestamp)
    }
    const parts=date["date-parts"][0]
    const [year, month, day] = date['date-parts'][0]
    if (day) {
      return new Date(Date.UTC(year, month - 1, day))
    } else if (month) {
      return new Date(Date.UTC(year, month - 1))
    } else {
      return new Date(Date.UTC(year))
    }
  }
  static bestDate(publi) {
    if (publi.issued != null) {
      return {type:"issued", dateInfo:publi.issued}
    }
    else {
      return {type:"created", dateInfo:publi.created}
    }
  }
}