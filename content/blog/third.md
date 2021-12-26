Title: Apache Superset from Scratch: Day 3 (Frontend Setup)
Date: 2021-12-25 10:20
Category: Review

In Day 3, I'm going to dive into setting up the frontend. In general, I'm quite new to the frontend ecosystem, so expect lots of tangents to fill in knowledge gaps along the way!

We'll start with the [Frontend section from CONTRIBUTING.MD](https://github.com/apache/superset/blob/master/CONTRIBUTING.md#frontend).

The first paragraph has some helpful historical context:

> Frontend assets (TypeScript, JavaScript, CSS, and images) must be compiled in order to properly display the web UI. The superset-frontend directory contains all NPM-managed frontend assets. Note that for some legacy pages there are additional frontend assets bundled with Flask-Appbuilder (e.g. jQuery and bootstrap). These are not managed by NPM and may be phased out in the future.

### Node

Thankfully, I've used Node a little bit before. Let me check what version I have installed on this computer. Usually the `--version` flag will do the trick!

```
node --version
> v17.3.0
```

The guide recommends Node 16, but Node 17.x should be fine. Let's check the `npm` version next. Npm is the Node package manager:

```
npm --version
> 8.3.0
```

The guide recommends using `nvm` to manage different Node versions. This is helpful advice, but I don't want to prematurely optimize and add more abstraction / complexity than needed. So let's soldier on for now.

### Package.json

The `package.json` is the Node equivalent to Python's `requirements.txt` file. For Superset, the `package.json` file lives within the `superset/superset-frontend/` folder. Let's switch into that folder.

What's actually in this file? A. LOT. Let's break some of this down.

```
{
  "name": "superset",
  "version": "0.0.0dev",
  "description": "Superset is a data exploration platform designed to be visual, intuitive, and interactive.",
  "keywords": [
    "big",
    "data",
    "exploratory",
    "analysis",
    "react",
    "d3",
    "airbnb",
    "nerds",
    "database",
    "flask"
  ],
```

This line is interesting: `"version": "0.0.0dev".` I wonder if this is where the Superset version value that's shown in the Superset UI lives? 

_As a quick detour, I wonder what this value in the `package.json` file [in the Superset v1.4 release](https://github.com/apache/superset/blob/1.4/superset-frontend/package.json) looks like?_

![Superset CLI]({static}/images/superset_14_package.png)

My hunch was right! 1.4 is harcoded as a string in the `package.json` file. Cool!

Then we can run `npm install`, which should use the `superset-frontend/package.json` file. But the documentation suggests `npm ci`. [Searching online suggests](https://stackoverflow.com/a/53325242) using `npm ci` if there's an existing `package-lock.json` file.

Because the project has an existing `package-lock.json` file, let's use `npm ci`!

![npm ci]({static}/images/npm_ci_1.png)

In the first half of the CLI output, I see that npm installed 5009 packages and displayed a bunch of deprecation warnings.

![npm ci]({static}/images/npm_ci_2.png)

In the second half of the CLI output, I see that there are 111 vulnerabilities. I'm noting both of these down (through this post!) to investigate later.

### Build Frontend Assets

Next, as the guide suggests, I will run `npm run build`. After a few minutes, I was presented with many warnings but some indication that the build succeeded?

![npm run build]({static}/images/npm_run_build.png)

Next, we can start the dev server at port `9000` by running:

```
npm run dev-server
```

Here's what the CLI output looks like with both the frontend and backend runinng simultaneously:

![backend and frontend]({static}/images/backend_frontend.png)

Exciting! Now if I head to `localhost:8088`, I should see Superset:

![Superset UI]({static}/images/superset_ui.png)

Hmm, that's curious. I'm logged in as the admin and I'm still seeing issues.

Unfortunately I'm out of time for today, so I'll have to debug this on Day 4!