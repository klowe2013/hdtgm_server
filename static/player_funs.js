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
    let {snd: b64buf} = await res.json()
    return b64buf
}

check_player_time = () => {
    // Returns current player time in seconds (e.g., 90 = 1 min 30s)
    return player.currentTime
}

change_player_time = (delta_seconds) => {
    player.currentTime += delta_seconds
}

let current_episode = ''
let current_chunk = 0
let playing_chunk = 0
let chunkData = []
let chunkLengths = []
let cumLength = 0
const nChunks = 3
let fullEpisode = ''

change_btn.addEventListener("click", function () {
    console.log('received click for audio buffer')
    current_chunk = 0
    chunkData = []
    chunkLengths = []
    load_episode(ep_selector.value)
});

load_episode = async (episode_id) => {
    let is_paused = play_btn.paused 
    play_btn.innerHTML = 'Loading...'
    current_episode = episode_id
    player.src = mp3_prefix
    for (i=0; i < nChunks; i++) {
        let thisChunk = await load_audio(current_episode, current_chunk)
        chunkData.push(thisChunk)
        console.log(fullEpisode.length/1000)
        fullEpisode += thisChunk
        current_chunk += 1
        delay(100)
    }
    current_chunk = nChunks
    play_btn.innerHTML = 'Pause'
    playNextChunk()
}

playNextChunk = async () => {
    const startTolerance = .1
    let playingBuff = chunkData.shift()
    player.src = `${mp3_prefix}${playingBuff}`
    let currentTime = player.currentTime
    // player.src += playingBuff
    // player.src = `${player.src}${playingBuff}`
    // player.src = `${mp3_prefix}${fullEpisode}`
    // player.currentTime = currentTime
    player.currentTime = startTolerance
    player.play()
    let thisChunk = await load_audio(current_episode, current_chunk)
    chunkData.push(thisChunk)
    current_chunk += 1
}

player.addEventListener("timeupdate", function() {
    const endTolerance = .1
    if (player.currentTime >= (player.duration - endTolerance)) {
        console.log(`caught end of chunk within tolerance; loading chunk ${current_chunk}`)
        chunkLengths.push(player.currentTime)
        playNextChunk()
    }
})


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

