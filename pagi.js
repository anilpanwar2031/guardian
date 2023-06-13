trs = [];
let ls = document.querySelectorAll('.ep');
let lastpage = 10;
console.log(lastpage);
for (let index = 0; index < lastpage; index++)
{
    let table = document.querySelector('.searchResults').querySelectorAll('tr');
    document.querySelector('.next').click();
    table.forEach((ele) =>
    { trs.push(ele) }
    )
};
    let table = document.querySelector('#eobResultsBox > table > tbody');
    trs.forEach((ele) =>
    { console.log(ele.innerText);
        table.appendChild(ele)
    })