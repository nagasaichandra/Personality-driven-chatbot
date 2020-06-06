# 582ircbot

Nagasai Chandra, Teja Kalvakolanu, Michael Fekadu

## [Demo][1]

## [Documentation][2]

## Getting Started

### 1. [Install Docker][3]

It works with Windows/macOS/Linux. No need for any virtual machines. Docker handles all of our infrastructure/dependency needs.

### 2. [Install Docker-Compose][4]

> Note: The previous step may have included the `docker-compose` binary depending on your operating system.

### 3. Clone this Repository

```
git clone https://github.com/mfekadu/582ircbot.git
```

### 4. Run all the services

The following command will run Rasa, the IRC worker bot, and the ElasticSearch service (the chatbot's memory):

Run the following command in the root of the directory for this codebase:

```
docker-compose up
```

> Note: ElasticSearch needs a lot of memory. If it crashes, try increasing docker's memory allocation to >= 4GB.

> Note: Grab a coffe or some snacks. The various downloads will take some time, but docker will _*cache*_ each stage of the build, so things will be faster next time.

[1]: #todo_insert_link
[2]: https://docs.google.com/document/d/1HJUQnLS-hRGTet0bFHm_5Sb3HJGqVXNRrpmMoM_1mDc/edit#heading=h.e2w1gjkkqb4z
[3]: https://docs.docker.com/get-docker/
[4]: https://docs.docker.com/compose/install/
[5]: #todo_insert_link
[6]: #todo_insert_link
[7]: #todo_insert_link
