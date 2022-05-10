/** @format */

import { readFile, writeFile } from "fs/promises"

let arcsData = JSON.parse(await readFile("../translated-arcs.json"))
let bookData = JSON.parse(await readFile("../chapters.json"))[0]

let arcsBuffer = arcsData.arcs.map((arc) => ({
	title: arc.title,
	number_of_chapters: arc.chapters.length,
	synopsis: arc.synopsis,
}))

let limits = []
let arcsLengths = arcsBuffer.map((arc) => arc.number_of_chapters)

arcsLengths.forEach((arcLength, index) => {
	if (index === 0) {
		limits.push(arcLength)
	} else if (index > 0) {
		let prevArcLength = limits[index - 1]
		limits.push(arcLength + prevArcLength)
	}
})

let arr = arcsData.arcs.map((arc, arcIdx) => {
	let [inf, sup] =
		arcIdx === 0 ? [0, limits[arcIdx]] : [limits[arcIdx - 1], limits[arcIdx]]
	let chapters = bookData.manga.chapters
		.slice(inf, sup)
		.map((chapter, chapterIdx) => {
			let title = arc.chapters[chapterIdx].title
			let mappedChapter = {
				number: chapter.number,
				title: title,
				number_of_pages: chapter.pages.length,
				time_ago: chapter.time_ago,
			}
			return mappedChapter
		})
	return {
		title: arc.title,
		number_of_chapters: arc.number_of_chapters,
		synopsis: arc.synopsis,
		chapters: chapters,
	}
})

let data = JSON.stringify([
	{
		name: bookData.manga.name,
		description: bookData.manga.description,
		content: arr,
	},
])

writeFile("mangas.json", data, (err) => {
	if (err) throw new Error(err)
	console.log("Data written in mangas.json file")
})
