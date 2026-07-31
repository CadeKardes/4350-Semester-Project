const loadingTips = [
  "Does anyone actually read these tips",
  "Good luck have fun!",
  "Don't hesitate to ask M365 Copilot",
  "Passwords are like toothbrushes. Don't share 'em!",
  "card game",
  "Hello World.",
  "SURVIVE",
  "You are now riding the bus.",
  "The best time to push your opponents is while they are reloading.",
  "Now enabling hard mode.",
  "So I just put the loading screen tips in here?",
  "Do not leave trees floating.",
  "Please note that Ride the Bus is not free to play. After a 40 day trial period you must either buy a license or stop playing.",
  "I have done nothing but write loading screen tips for 3 days.",
  "Look behind you.",
  "Geometry Dash is a terrible game.",
  "We will never ask for your password",
  "We will add a battle pass in the next sprint.",
  "Try to beat the Time Trial staff ghost!",
  "spend money",
  "99% of gamblers quit right before they hit big.",
  "Let's go gambling.",
  "Always bet on black.",
  "You can create more than one account on the same machine. Do not take advantage of this.",
  "Ask your parents before playing this game.",
  "Our time on this earth is fleeting.",
  "~80% of people that play this game are not subscribed.",
  "Use phantom membranes to repair your elytra.",
  "Ride the Bus is a data harvester.",
  "Boarding the bus...",
  "I am a loading screen",
  "You just lost The Game.",
  "Be aware of your elemental strengths and weaknesses.",
  "You can do it!",
  "Bet $1,987 for a special surprise!",
  "Most of the loading screen tips are false.",
  "Ride the Bus requires a functioning device camera to run.",
  "Bum, bum, be-dum, bum, bum be-dum, bum",
  "We can't give you money. Stop asking.",
  "Losing money in Ride the Bus also makes you lose money in real life.",
  "Have you ever played Ride the Bus with your life on the line?",
  "Call me. XOXO",
  "Press ESC to open your inventory.",
  "He is behind the loading bar.",
  "Add 'Dev_' to your username lets you win more often.",
  "Vote Ride the Bus for Game of the Year.",
  "Rolling gives you intangibility. Use it often!",
  "This tip has a .00001% chance of appearing.",
  "Press Ctrl + U on any website to hack it.",
  "The meaning of life is",
  "Don't get banned",
  "Ouuu, you want to bet $5,000 right now....",
  "Every instance of Ride the Bus is personalized.",
  "The Ride the Bus API key is Bvm8pGEu8yFOUAVOrP8ba4iEKew2J78g",
  "Let us commence forth.",
  "34.130.255.131",
  "This does not actually load anything.",
  "You will own nothing and be happy.",
  "Type 'BIG MONEY' in the chat to guarantee a win!",
  "Hold out your knife to move faster.",
  "Do not mute the music.",
  "You have unlocked a special poem!",
  "Server maintenance is scheduled at 4:00 AM EST",
  "This statement is false.",
  "Ride the Bus's chat is moderated. Don't say bad words!",
  "Ride the Brig.",
  "Remember: the game is fixed.",
  "Charge your phone",
  "Now enabling: Manual breathing and blinking",
  "Those cards aren't gonna flip themselves.",
  "Ctrl + Shift + Alt + Win + L",
  "There is a finite supply of cards.",
  "You are first in line.",
  "We have removed the ability to withdraw.",
  "A prankster comet has appeared!",
  "Updating localization files...",
  "The next live event will take place on 8/29/2026 8:00 PM EST",
  "Some attacks leave you wide open, but pack a heavy punch.",
  "Experiment with different heroes to find your perfect play style.",
  "Crouching and sneaking lowers the rate at which enemies detect you.",
  "Reusing passwords compromises your account security.",
  "You are a pirate.",
  "Listen to this game's original soundtrack on Spotify.",
  "What's a sprint to a scrum?",
  "Let's make some money",
  "Reach out to our team to request new features. We will think about them.",
  "You have unlocked Free Roam mode.",
  "Free money generator -> google.com/search?q=troll+face",
  "Don't overthink it",
  "Strictly for adults.",
  "Block your enemies' attacks at the right moment to perform a perfect guard.",
  "This game is green for an amazing reason.",
  "Some of these loading screen tips are problematic. I should remove some.",
  "There is no such thing as a coincidence. The fact that you are reading this means that you are energetically aligned with me and this message.",
  "Wash behind your ears.",
  "Every 60 seconds in Africa, a minute passes.",
  "This loading tip loves you.",
  "On account creation, you have a 1% chance to play as the dealer.",
  "Use W, A, S, D to move.",
  "Go outside",
  "You need an electronic device to play this game.",
  "What's up?",
  "Play at 3:00 AM to unlock Evil Ride the Bus.",
  "You have to have a very high IQ to understand Ride the Bus.",
  "The King of Heart's name is Mike.",
  "This game is so retro.",
  "Use practice mode to learn the layout of a level",
  "You can't win 'em all.",
  "Type 'patience' on this screen to skip.",
  "Sunny days mean blue skies.",
  "View all these loading tips for an achievement!",
  "Double jump while in the air.",
  "You don't actually make any money playing this game.",
  "Winning too many times in a row leads to an account ban.",
  "placeholder",
  "Please keep the chat related to Ride the Bus.",
  "Read our lorebook",
  "There are cards in this game.",
  "Jump right after a dash to conserve its momentum.",
  "Obtain a P-Rank on all levels for a secret reward.",
  "Click 'How to Play' to learn how to play.",
  "Dot dot dot",
  "What is this, some kind of Ride the Bus?",
  "Turn off your monitor to see the coolest person in the room.",
  "Input Up, Up, Down, Down, Left, Right, Left, Right, B, A, ENTER to enable debug mode.",
  "Bumping into walls causes your car to briefly decelerate.",
  "https://imgur.com/a/0u60rWz",
  "There is a limited supply of pity cash",
  "Collect my pages.",
  "Made with Rust.",
  "If fighting is sure to result in victory, you must fight.",
  "Check your email",
  "Are you winning?",
  "Don't you have anything better to do?",
  "Our lawyers have advised us to not write this tip.",
  "A loading screen is a user interface element that appears while a computer program, application or video game completes background process or system initialization. Its purpose is to inform users that their system is still working and to provide feedback during delay. Loading screens may display animated graphics, rotating symbols or other indicators while complex calculations takes place in the background. As the internet became more accessible, two common types of loading indicators became widely used: the throbber, an animated icon that signifies ongoing activity, and the progress bar, a linear visual element that estimates the completion status and remaining loading time.",
  "You are more likely to win lotteries on sundays.",
  "You are running an illegally obtained copy of this game.",
  "What are you looking at?",
  "You can now play as Luigi.",
  "Let's get back on track.",
  "This game is not for the faint of heart.",
  "The item shop refreshes every midnight, UTC time.",
  "Are you having fun yet?",
  "Wake up."
];

function getRandomLoadingTip() {
  return loadingTips[Math.floor(Math.random() * loadingTips.length)];
}

function resetLoadingBar() {
  const fill = document.getElementById('loading-fill');
  fill.style.transition = 'none';
  fill.style.width = '0%';
  void fill.offsetWidth;
  fill.style.transition = 'width 0.05s linear';
}

function startLoading() {
  const loadingScreen = document.getElementById('loading-screen');
  if (!loadingScreen) return;
  loadingScreen.classList.remove('hidden');

  resetLoadingBar();

  const fill = document.getElementById('loading-fill');
  const status = document.getElementById('loading-status');
  status.textContent = getRandomLoadingTip();

  let progress = 0;
  const duration = Math.floor(1000 + Math.random() * 1501); // 1s to 2.5s
  const stepTime = 40;
  const stepSize = 100 / (duration / stepTime);

  const timer = setInterval(() => {
    progress += stepSize;
    if (progress > 100) progress = 100;

    fill.style.width = progress + '%';

    if (progress >= 100) {
      clearInterval(timer);
      setTimeout(() => {
        loadingScreen.classList.add('hidden');
      }, 250);
    }
  }, stepTime);
}

startLoading();
