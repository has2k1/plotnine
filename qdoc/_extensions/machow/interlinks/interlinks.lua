--- Interlinks
---
--- This extension converts incomplete links into complete links
---
--- An incomplete link type, missing a uri
--- Internally we represent that link as follows
--- @alias ilinkT
--- | { name: string, role: string?, domain: string?, inv_name: string?, external: boolean?, shortened: boolean? }
--- Any other fields are irrelevant
---
--- A complete link type, has a uri
--- For links to this project, the uri is a relative path from  documentation root.
--- For links to other projects, the uri is a full url (including the domain)
--- @alias clinkT
--- | { uri: string, name: string, role: string?, domain: string?, inv_name: string? }
--- Any other fields are irrelevant

-- Local references to all the global variables we expect to be available
local quarto = _G.quarto --- @diagnostic disable-line:undefined-field
local pandoc = _G.pandoc --- @diagnostic disable-line:undefined-field

-- quartodoc documentation directory
local qdoc_root = quarto.project.offset

-- The hex representation of a quote (`) is %60
-- lua requires %% to represent %
local HEX_QUOTE = "%%60"

--[[
A table of all known complete links

It should include links for:

  1. This project
  2. Other python projects

The keys are the names of the links i.e.

  inventory["pkg.mod.cls"] = { { name = "pkg.mod.cls", ... }, ...}
  inventory["some_label"] = { { name = "some_label", role = "label", ... }, ... }
]]
--- @type table<string, clinkT[]>
local inventory = {}
local CACHE_FILENAME = qdoc_root .. "/.quarto/interlinks/inventory.json"


--- Check if file exists
---
--- @param filename string
--- @return boolean
local function file_exists(filename)
  local f = io.open(filename, "r")
  if f then
    io.close(f)
    return true
  else
    return false
  end
end

--- Write to file
--- Creates directories as required
---
--- @param filename string
--- @param content string
local function write_to_file(filename, content)
  local dir = filename:gsub ("[^/]+$", "")
  pandoc.system.make_directory(dir, true)

  local file = io.open(filename, "w")
  assert(file)
  file:write(content)
  file:close()
end

--- Write to file
---
--- @param filename string
--- @return string # content of the file
local function read_from_file(filename, read_params)
  if not read_params then
    read_params = "a"
  end

  local file = io.open(filename, "r")
  assert(file)
  local content = file:read(read_params)
  file:close()
  return content
end


--- Add a source of links to the inventory
---
--- @param filename string
--- @param prefix string A prefix to the original uris in the source file
---   so that they are resolvable.
---   For external links, it should be the source url
---   For internal links, it should be a "/".
local function add_link_source_to_inventory(filename, prefix)
  local contents = read_from_file(filename, "a")

  -- NOTE: Down the line, change to pandoc.json.decode as
  -- it now exposes the same method.
  local json = quarto.json.decode(contents)

  if not json then
    return
  end

  prefix = prefix or ""

  for _, item in ipairs(json.items) do
    item.uri = prefix .. item.uri
    if inventory[item.name] then
      table.insert(inventory[item.name], item)
    else
      inventory[item.name] = {item}
    end
  end
end


--- Build inventory index from the sources
---
--- @param sources table[]
local function build_inventory(sources)
  local filename
  local prefix
  for _, item in pairs(sources) do
    filename, prefix = item[1], item[2]
    add_link_source_to_inventory(filename, prefix)
  end
end


--- Write inventory to file cache
---
local function write_inventory_cache()
  local json = quarto.json.encode(inventory)
  write_to_file(CACHE_FILENAME, json)
end


--- Load inventory from the file cache
local function read_inventory_cache()
  if not file_exists(CACHE_FILENAME) then
    return {}
  end

  local contents = read_from_file(CACHE_FILENAME)
  local json = quarto.json.decode(contents)
  return json
end


--- Search for a complete link in inventory file
---
--- @param ilink ilinkT An incomplete link
--- @return clinkT | nil # A complete link, if one is found
local function lookup_complete_link(ilink)
  -- Matching process
  -- 1. Get all links with the same name
  -- 2. Filter out links whose other attributes (inv_name, role, domain)
  --    do not match. Ignore attributes that are missing in the ilink.
  local results = {}
  local candidates = inventory[ilink.name] or {}
  local attributes_match

  for _, item in ipairs(candidates) do
    attributes_match = not (
      -- e.g. :external+<inv_name>:<domain>:<role>:`<name>`
      (item.inv_name and item.inv_name ~= ilink.inv_name) or
      (ilink.role and item.role ~= ilink.role) or
      (ilink.domain and item.domain ~= ilink.domain)
    )

    if attributes_match then
      table.insert(results, item)
    end
  end

  if #results == 1 then
    return results[1]
  end

  if #results > 1 then
    print("Found multiple matches for " .. ilink.name)
    quarto.utils.dump(results)
  elseif #results == 0 then
    print("Found no matches for object:")
    quarto.utils.dump(ilink)
  end

  return nil
end


--- Split string on a given separator
---
--- @param str string String to split
--- @param sep string Separator. If none, then empty spaces
--- @return string[] # tokens of the input string
local function split_on(str, sep)
  local tokens = {}
  sep = sep or "%s"

  for s in string.gmatch(str, "([^"..sep.."]+)") do
    table.insert(tokens, s)
  end

  return tokens
end


--- Change unstandard role names to their standard values
--- Any common abbreviations for roles that are not standard should
--- handled here.
---
--- @param role string Name of role to make standard
--- @return string # The standard form of a role
local function standardize_role(role)
  if role == "func" then
    return "function"
  end

  return role
end


--- Convert a markup "link" string to an incomplete link
--- @param str string Markup
--- @return ilinkT
local function as_incomplete_link(str)
  local ilink = {}
  local starts_with_colon = str:sub(1, 1) == ":"
  local quoted_text_pattern = HEX_QUOTE.."(.*)"..HEX_QUOTE

  if starts_with_colon then
    local tokens = split_on(str, ":")

    if #tokens == 2 then
      -- e.g. :func:`my_func`
      ilink.role = standardize_role(tokens[1])
      ilink.name = tokens[2]:match(quoted_text_pattern)
    elseif #tokens == 3 then
      -- e.g. :py:func:`my_func`
      ilink.domain = tokens[1]
      ilink.role = standardize_role(tokens[2])
      ilink.name = tokens[3]:match(quoted_text_pattern)
    elseif #tokens == 4 then
      -- e.g. :ext+inv:py:func:`my_func`
      ilink.external = true
      ilink.inv_name = tokens[1]:match("external%+(.*)")
      ilink.domain = tokens[2]
      ilink.role = standardize_role(tokens[3])
      ilink.name = tokens[4]:match(quoted_text_pattern)
    end
  else
    ilink.name = str:match(quoted_text_pattern)
  end

  if not ilink.name then
    print("couldn't parse this link: " .. str)
    return {}
  end

  if ilink.name:sub(1, 1) == "~" then
    ilink.shortened = true
    ilink.name = ilink.name:sub(2, -1)
  end
  return ilink
end


--- Get the string content a link
--- Used as a fallback for broken links
--- @param link table pandoc link
local function get_link_content(link)
  return pandoc.Code(pandoc.utils.stringify(link.content))
end


--- Do the actual interlinking
---
--- @param link table pandoc link
--- @param ilink ilinkT incomplete link representation of link target
--- @param clink clinkT complete link representation of link target
local function do_interlink(link, ilink, clink)
  local original_text = pandoc.utils.stringify(link.content)

  -- determine replacement, use if link text is not specified
  local replacement
  if ilink.shortened then
    local tokens = split_on(ilink.name, ".")
    replacement = tokens[#tokens]
  else
    replacement = ilink.name
  end

  -- set link text
  if replacement and original_text == "" then
    link.content = pandoc.Code(replacement)
  end

  link.target = clink.uri:gsub("%$$", ilink.name)
end


--- Process .qmd meta and build inventory from the source
--- @param meta table pandoc.Meta
local function Meta(meta)
  if not next(inventory) and file_exists(CACHE_FILENAME) then
    inventory = read_inventory_cache()
    return
  end

  local filename = qdoc_root .. "/objects.json"
  local prefix
  local sources = {
    { filename, "/" },
  }

  for k, v in pairs(meta.interlinks.sources) do
    filename = qdoc_root .. "/_inv/" .. k .. "_objects.json"
    prefix = pandoc.utils.stringify(v.url)
    table.insert(sources, {filename, prefix})
  end

  build_inventory(sources)
  write_inventory_cache()
end


--- Process link
--- @param link table pandoc.Link
local function Link(link)
  -- Regular links remain unchanged
  if not link.target:match(HEX_QUOTE) then
    return nil
  end

  -- lookup item
  local ilink = as_incomplete_link(link.target)
  local clink = lookup_complete_link(ilink)

  -- broken links
  if not clink then
    return get_link_content(link)
  end

  do_interlink(link, ilink, clink)
  return link
end


return {
  -- The functions are called in the order they appear here
  { Meta = Meta },
  { Link = Link },
}
