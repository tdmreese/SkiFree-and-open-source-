
//ross-y skiis are yellow/orange
//atomic skiis are red
//dynastar skiis are blue

const canvas = document.getElementById("skiCanvas")
canvas.width = 640
canvas.height = 540
const ctx = canvas.getContext("2d")

//facing ranges from -2,-1,0,1,2
let player = {
    xPos: 128,
    yPos: 128,
    state: "waiting",
    facing: 1
}

let tree1 = {
    posX: 480,
    posY: 480,
    size: 3
}

let allPlayers = []
let obstacles = []

function setup(){
    pass
}

let aJump = {
    posX: 140,
    posY: 240,
}

draw()

//draw everything
function draw(){

    ctx.save()
    drawSkier()
    drawTree(tree1)
    drawJump(aJump)
    
    // drawBackground()
    // drawSquares()

    //translate methods are additive, so we restore the canvas to the localState before the last save method so we don't shift things off screen
    ctx.restore()
}

function drawJump(aJump){
    ctx.beginPath()

    let jumpWidth = 64

    // Create linear vertical gradient
    const grad=ctx.createLinearGradient(aJump.posX-jumpWidth/2, aJump.posY-jumpWidth/2, aJump.posX-jumpWidth/2, aJump.posY);
    grad.addColorStop(0, "lightblue");
    grad.addColorStop(1, "#34abeb");

    // Fill rectangle with gradient
    ctx.fillStyle = grad;
    ctx.fillRect(aJump.posX- jumpWidth/2, aJump.posY-jumpWidth/2, jumpWidth, (jumpWidth/2));

    ctx.lineWidth = 4
    ctx.strokeStyle = "#34abeb"

    ctx.moveTo(aJump.posX - jumpWidth/2, aJump.posY)
    ctx.lineTo(aJump.posX + jumpWidth/2, aJump.posY)
    ctx.stroke()

    // ctx.lineWidth = 2
    ctx.moveTo(aJump.posX - jumpWidth/2, aJump.posY)
    ctx.lineTo(aJump.posX - jumpWidth/2, aJump.posY + 16)

    ctx.moveTo(aJump.posX + jumpWidth/2, aJump.posY)
    ctx.lineTo(aJump.posX + jumpWidth/2, aJump.posY + 16)
    ctx.stroke()

}

function drawTree(aTree){
    ctx.beginPath()
    ctx.lineWidth = 2
    let treeSize = 8
    let stumpSize = 20
    //stump
    ctx.strokeStyle = "#d17f45"
    ctx.strokeRect(aTree.posX - stumpSize/2, aTree.posY - stumpSize/2, 20,20);
    
    //leaves and branches
    ctx.strokeStyle = "green"
    for(let i = 0; i < treeSize; i++){
        ctx.moveTo(aTree.posX - 4 * (treeSize - i), aTree.posY - 8 * i)
        ctx.lineTo(aTree.posX + 4 * (treeSize - i), aTree.posY - 8 * i)
        ctx.stroke()
    }

}

function drawSkier(){
    drawSkiis()
    drawHead()
    drawBody()
}

function drawHead(){
    ctx.beginPath()
    ctx.arc(player.xPos, player.yPos-32, 12, 0, 2 * Math.PI);
    ctx.fillStyle = "white";
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "black";
    ctx.closePath()
    ctx.stroke();
}

function drawBody(){
    //body
    ctx.beginPath()
    ctx.lineWidth = 2;
    ctx.strokeStyle = "black";
    ctx.moveTo(player.xPos-8, player.yPos-20)
    ctx.lineTo(player.xPos-8, player.yPos-6)
    ctx.lineTo(player.xPos+8, player.yPos-6)
    ctx.lineTo(player.xPos+8, player.yPos-20)
    //legs
    ctx.moveTo(player.xPos-7, player.yPos-6)
    ctx.lineTo(player.xPos-7, player.yPos+4)
    
    ctx.moveTo(player.xPos+7, player.yPos-6)
    ctx.lineTo(player.xPos+7, player.yPos+4)
    
    ctx.stroke()
}

function drawSkiis(){
    ctx.beginPath()
    ctx.lineWidth = 2
    ctx.strokeStyle = "red"
    switch(player.facing){
        case -2:
            lineWidth = 3
            ctx.moveTo(player.xPos-16, player.yPos+4)
            ctx.lineTo(player.xPos+12, player.yPos+4)
            break
        case -1:
            ctx.moveTo(player.xPos+12, player.yPos)
            ctx.lineTo(player.xPos, player.yPos+8)
            //stage right ski
            ctx.moveTo(player.xPos, player.yPos)
            ctx.lineTo(player.xPos-12, player.yPos+8)
            break
        case 0:
            ctx.moveTo(player.xPos-7, player.yPos)
            ctx.lineTo(player.xPos-7, player.yPos+10)
            //stage right ski
            ctx.moveTo(player.xPos+7, player.yPos)
            ctx.lineTo(player.xPos+7, player.yPos+10)
            break
        case 1:
            ctx.moveTo(player.xPos-12, player.yPos)
            ctx.lineTo(player.xPos, player.yPos+8)
            //stage right ski
            ctx.moveTo(player.xPos, player.yPos)
            ctx.lineTo(player.xPos+12, player.yPos+8)
            break
        case 2:
            lineWidth = 3
            ctx.moveTo(player.xPos+16, player.yPos+4)
            ctx.lineTo(player.xPos-12, player.yPos+4)
            break

    }
    ctx.stroke()
}

