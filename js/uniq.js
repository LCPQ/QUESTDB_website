function uniq(array)
{
   if (array.length == 0) return [];
   const sortedArray = array.map( x => [JSON.stringify(x), x] ).sort();
   var uniqueArray = [ sortedArray[0][1] ];
   for (let i=1 ; i<sortedArray.length ; i++) {
     if ( sortedArray[i][0].localeCompare(sortedArray[i-1][0]) != 0 )
       uniqueArray.push(sortedArray[i][1])
   }
   return uniqueArray;
}
