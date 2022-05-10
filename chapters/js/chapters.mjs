/** @format */

import { readFile, writeFile } from "fs/promises"

let mangaData = JSON.parse(await readFile("./mangas.json"))[0].content
let bookData = JSON.parse(await readFile("../chapters.json"))[0].manga.chapters

let chapterMappedArcs = mangaData.map((arc) => ({
	chapters: arc.chapters,
	title: arc.title,
}))

let arcMappedChapters = chapterMappedArcs.flatMap((arc, arcIdx) => {
	const mappedChapters = arc.chapters.map((chapter) =>
		Object.assign({}, { number: chapter.number, arc: arc.title })
	)
	return mappedChapters
})

let chapters = arcMappedChapters.map((chapter, chapterIdx) => {
	return Object.assign({}, { ...chapter, pages: bookData[chapterIdx].pages })
})

let data = JSON.stringify([{ name: "Black Clover", chapters }])

writeFile("chapters.json", data, (err) => {
	if (err) throw new Error(err)
	console.log("Data written in mangas.json file")
})
