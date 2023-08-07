# AutoReloader
 WARNING: THIS SCRIPT IS IN VERY INCOMPLETE STATE. IT HAS A LOT REFINING TODO. ALSO MIGHT WORK BUGGY IN WINDOWS. 

# Change Log
<details>
 <summary><b>7 August 2023</b></summary>
 <br>
With last update now it has server capabilities thanks to PHP's built in server. Also code is more readable now and did some error handling. Cleaned unnecessary imports. I will try to make it look better. <br> It might be much more buggy then it was before in Windows because I didn't test any of these features if they work on Windows soooo if you encounter any bugs please report.
</details>

 
 ## What is this script about? 
Hey, this is an old and early stage script that I use for auto reloading web pages in a browser thanks to selenium. It basically follows changes done in the directory and redirects the page if any changes done in the file. It has basic built in commands to ignore files or paths. (I might add ignore file types too. It's not hard but never needed it.) Also some fancy features. This script was all about reloading and nothing else, I upgraded it a little bit. Added new commands and capabilities.
 #### What is this capabilities? 
It has ability to add and change commands on fly! You can add, delete or modify commands while the script is running. Just edit commandhandler.py.

 ## Why I'm publishing it?
Well, mostly I hope it's going to help others. I mean frameworks like Laravel or node.js has better built-in server capabilities with auto reloading/redirecting skill but this also works! I wanted to create a project that is both understandable and usable in real life. Most of the begginer projects are not usable.

 ## How this works? 
It's quite simple. Run the executer.py file. There's some CLI args for the executer.py. Use "-h" to print help and get CLI args. Also it has built in commands. Use "help" to print help and get command list.

# **NOTE**
~~This requries a running web server. Like apache, Live Server, laravel artisan, etc. I might add a server feature but it's not there yet so you need to use a server for loading your pages. I use it with XAMPP's apache setup. Quite easy to install and works fine.~~ New Update: Now it has it's own server capabilities if you have PHP installed on your computer. But can and will continue to run with other server's too. It's still using Selenium's driver to load pages and as long as they are loadable, this script will do it's job. I'll try to add PHP's server capabilities in this folder so it can be shipped with PHP Built-in Development Server in it like Laravel Artisan.

I'm aiming to an alternative server that can work with npm's server for React. So it will use npm to load pages etc etc. 

 ### Wdym by buggy in Windows?
Initially I wrote this in Linux. And I cleaned and optimized the code for Linux use only. Since I decided to publish this I tried to run on Windows and it was meh. Did a little bit tinkering and it works *just fine*. But it hurt code's readability. Didn't refine it yet. It's just too much work. I might refine and publish another update for windows later, in my spare time.
