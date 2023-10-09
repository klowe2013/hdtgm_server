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
    const res = await fetch(`/audio_by_id/${episode_id}_${chunk_no}`);
    audioJson = await res.json()
    return audioJson
}

check_player_time = () => {
    // Returns current player time in seconds (e.g., 90 = 1 min 30s)
    return player.currentTime
}

change_player_time = (delta_seconds) => {
    player.currentTime += delta_seconds
}

let current_episode = ''
let loadChunk = 0
let playChunk = 0
let chunkData = [0]
let chunkLengths = [0]
let cumLength = 0
const nChunks = 3

change_btn.addEventListener("click", function () {
    console.log('received click for audio buffer')
    loadChunk = 0
    chunkData = [0]
    chunkLengths = [0]
    playChunk = 0
    load_episode(ep_selector.value)
});

let fullDuration = 0
load_episode = async (episode_id) => {
    let is_paused = play_btn.paused 
    play_btn.innerHTML = 'Loading...'
    current_episode = episode_id
    res = await fetch(`/get_episode_length/${episode_id}`)
    let {full_duration: duration_res} = await res.json()
    fullDuration = duration_res
    console.log(`${episode_id} has length ${fullDuration}`)
    player.src = mp3_prefix
    for (i=0; i < nChunks; i++) {
        let audioJson = await load_audio(current_episode, loadChunk)
        chunkData.push(audioJson.snd)
        chunkLengths.push(audioJson.chunk_len + chunkLengths[chunkLengths.length - 1])
        loadChunk += 1
        delay(100)
    }
    loadChunk = nChunks
    play_btn.innerHTML = 'Pause'
    playNextChunk()
}

playNextChunk = async () => {
    const startTolerance = .1
    playChunk += 1
    let playingBuff = chunkData[playChunk]
    player.src = `${mp3_prefix}${playingBuff}`
    player.currentTime = startTolerance
    player.play()
    if (playChunk > (loadChunk - nChunks)) {
        let thisChunk = await load_audio(current_episode, loadChunk)
        chunkData.push(thisChunk)
        loadChunk += 1
    }   
}

// Update progress bar
function updateProgress(e) {
    const endTolerance = .1
    const { duration, currentTime } = e.srcElement;
    if (currentTime >= (duration - endTolerance)) {
        console.log(`caught end of chunk within tolerance; loading chunk ${current_chunk}`)
        cumLength += player.currentTime
        chunkLengths.push(cumLength)
        playNextChunk()
    } else {
        const progressPercent = ((currentTime + chunkLengths[playChunk-1]) / fullDuration) * 100;
        progress.style.width = `${progressPercent}%`;
    }
}

// Set progress bar
const progress = document.getElementById('progress');
const progressContainer = document.getElementById('progress-container');
async function setProgress(e) {
    const width = this.clientWidth;
    const clickX = e.offsetX;
    const duration = player.duration;

    let desired_time = (clickX / width) * fullDuration

    console.log(`would set time to ${desired_time}`)

    const params = {'target_time': desired_time}
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
            console.log(`Catching up to chunk ${myChunk} to get to ${desired_time}: currently at ${loadChunk} (${chunkLengths[chunkLengths.length - 1]})`)
            let audioJson = await load_audio(current_episode, loadChunk)
            chunkData.push(audioJson.snd)
            chunkLengths.push(audioJson.chunk_len + chunkLengths[chunkLengths.length - 1])
            loadChunk += 1
            delay(100)
        }
    }

    playChunk = myChunk 
    chunkStart = chunkLengths[playChunk-1]
    chunkTime = desired_time - chunkStart
    let playingBuff = chunkData[playChunk]
    player.src = `${mp3_prefix}${playingBuff}`
    player.currentTime = chunkTime
    player.play()

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

