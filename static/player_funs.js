const change_btn = document.getElementById("change_button");
const play_btn = document.getElementById("play")
const ep_selector = document.getElementById("episode_selector");
const player = document.getElementById('audio_player')
const mp3_prefix = "data:audio/mp3;base64, "
let audio_buffer = ""

function delay(milliseconds){
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}

load_audio = async (episode_id, chunk_no) => {
    console.log(`Loading episode id ${episode_id}, chunk ${chunk_no}`)
    let globalTimeSave = globalTime
    const res = await fetch(`/audio_by_id/${episode_id}_${chunk_no}`);
    audioJson = await res.json()
    globalTime = globalTimeSave 
    return audioJson
}

check_player_time = () => {
    // Returns current player time in seconds (e.g., 90 = 1 min 30s)
    return player.currentTime
}

let current_episode = ''
let globalTime = 0
let loadChunk = 0
let playChunk = 0
// let chunkLengths = [0]
let chunkLengths = new Map([[0,  0]])
let chunkMap = new Map([[0,  '']])
let cumLength = 0
const nChunks = 3
const progWidth = 400

change_btn.addEventListener("click", function () {
    console.log('received click for audio buffer')
    loadChunk = 0
    chunkLengths = new Map([[0,  0]])
    chunkMap = new Map([[0,  '']])
    playChunk = 0
    globalTime = 0
    load_episode(ep_selector.value)
});

let fullDuration = 0
load_episode = async (episode_id) => {
    let is_paused = play_btn.paused 
    play_btn.innerHTML = 'Loading...'
    current_episode = episode_id
    console.log(`before awaiting episode length the global value is ${globalTime}`)
    res = await fetch(`/get_episode_length/${episode_id}`)
    console.log(`after awaiting episode length the global value is ${globalTime}`)
    let {full_duration: duration_res} = await res.json()
    fullDuration = duration_res
    console.log(`${episode_id} has length ${fullDuration}`)
    
    // Set src to blank
    player.src = mp3_prefix
    // Load nChunks buffer
    for (i=0; i < nChunks; i++) {
        loadChunk += 1
        let audioJson = await load_audio(current_episode, loadChunk)
        chunkMap.set(loadChunk, audioJson.snd)
        chunkLengths.set(loadChunk, audioJson.chunk_len + chunkLengths.get(loadChunk-1))
        delay(100)
    }
    loadChunk = nChunks
    play_btn.innerHTML = 'Pause'
    playNextChunk()
}

// Update progress bar
function updateProgress(e) {
    const endTolerance = .1
    const { duration, currentTime } = e.srcElement;
    if (currentTime >= (duration - endTolerance)) {
        console.log(`caught end of chunk within tolerance; loading chunk ${loadChunk}`)
        // cumLength += player.currentTime
        chunkLengths.set(playChunk, globalTime)
        playNextChunk()
    } else {
        globalTime = currentTime + chunkLengths.get(playChunk-1)
        const progressPercent = ((globalTime) / fullDuration) * 100;
        progress.style.width = `${progressPercent}%`;
        // progress.style.width = `${Math.floor(progressPercent*progWidth)}px`
    }
}

change_player_time = async (delta_seconds) => {
    let relativeTime = player.currentTime + delta_seconds
    let desiredTime = globalTime + delta_seconds
    
    if (relativeTime > 0 && relativeTime < player.duration) {
        // If we're in the right chunk, no problem
        player.currentTime += delta_seconds
    } else {
        // If not, we have to find the right chunk and load it
        const params = {'target_time': desiredTime}
        const options = {
            'method': 'POST',
            'body': JSON.stringify(params),
            'headers': {'content-type': 'application/json'}
        }
        chunkRes = await fetch(`/find_chunk/${current_episode}`, options)
        chunkJson = await chunkRes.json()
        let myChunk = chunkJson.search_chunk
    
        if (myChunk >= loadChunk) {
            // Loop and load chunks to get to myChunk
            const startChunk = loadChunk
            for (i=startChunk; i <= myChunk; i++) {
                let audioJson = await load_audio(current_episode, loadChunk)
                chunkMap.set(loadChunk, audioJson.snd)
                console.log(`setting chunk length for ${loadChunk} to ${audioJson.chunk_len + chunkLengths.get(loadChunk-1)}`)
                chunkLengths.set(loadChunk, audioJson.chunk_len + chunkLengths.get(loadChunk-1))
                loadChunk += 1
                delay(100)
            }
        }
        let origChunk = playChunk
        playChunk = myChunk - 1
        chunkStart = chunkLengths.get(playChunk-1)
        chunkTime = desiredTime - chunkStart
        console.log(`Setting global time to ${desiredTime}, which is ${relativeTime} relative to chunk ${origChunk} and ${chunkTime} into chunk ${myChunk} which starts at ${chunkStart}`)
        globalTime = desiredTime 
        let playingBuff = chunkMap.get(playChunk)
        player.src = `${mp3_prefix}${playingBuff}`
        player.currentTime = chunkTime
        player.play()
        play_btn.innerHTML = 'Pause'
    }
}

// Set progress bar
const progress = document.getElementById('progress');
const progressContainer = document.getElementById('progress-container');
async function setProgress(e) {
    const width = this.clientWidth;
    const clickX = e.offsetX;
    
    let desiredTime = (clickX / width) * fullDuration
    let deltaTime = desiredTime - globalTime

    console.log(`would set time to ${desiredTime} (delta = ${deltaTime})`)

    play_btn.innerHTML = 'Loading...'
    
    change_player_time(deltaTime)

}
  
playNextChunk = async () => {
    const startTolerance = .1
    playChunk += 1
    let playingBuff = chunkMap.get(playChunk)
    player.src = `${mp3_prefix}${playingBuff}`
    player.currentTime = startTolerance
    player.play()
    console.log(`About to reset global time; playChunk is ${playChunk} and its start is ${chunkLengths.get(playChunk)}`)
    globalTime = chunkLengths.get(playChunk)
    console.log(`global time is now set to ${globalTime}`)
    if (playChunk > (loadChunk - nChunks)) {
        let audioJson = await load_audio(current_episode, loadChunk)
        console.log(`global time is now set to ${globalTime} after awaiting load_audio`)
        chunkMap.set(loadChunk, audioJson.snd)
        console.log(`In playNextChunk setting time: globalTime is ${globalTime}, prev time is ${chunkLengths.get(loadChunk-1)} and current length is ${audioJson.chunk_len}`)
        chunkLengths.set(loadChunk, audioJson.chunk_len + chunkLengths.get(loadChunk-1))
        console.log(chunkLengths)
        loadChunk += 1
    }   
}


  
player.addEventListener("timeupdate", updateProgress)

// Click on progress bar
progressContainer.addEventListener('click', setProgress);

play_btn.addEventListener("click", function () {
    if (player.paused) {
        player.play()
        play_btn.innerHTML = 'Pause'
    } else {
        player.pause()
        play_btn.innerHTML = 'Play'
    }
})

download_curr_episode = () => {
    let episode_id = ep_selector.value 
    let episode_name = ep_selector.options[ep_selector.selectedIndex].text
    let filename = `${episode_name}.mp3`
    fetch(`/download_by_id/${episode_id}`)
        .then((res)=>{
            return res.blob()
        }).then((blob)=>{
           let el = document.createElement("a"); 
           // creates anchor element but doesn't add it to the DOM
           el.setAttribute("download", [filename]) 
           // make the link downloadable on click
           let url = URL.createObjectURL(blob); 
           // creates a url to the retrieved file
           el.href = url; // set the href attribute attribute
           el.click(); 
           URL.revokeObjectURL(url)
        })
    // catch errors
    .catch(err=>console.log(err));
}

