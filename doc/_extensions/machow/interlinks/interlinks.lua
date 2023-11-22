--- Interlinks
---
--- This extension converts incomplete links into complete links
---
--- An incomplete link type, missing a uri
--- Internally we represent that link as follows
--- @alias ilinkT
--- | { name: string, role: string, domain: string, inv_name: string?, external: boolean?, shortened: boolean? }
--- Any other fields are irrelevant
---
--- A complete link type, has a uri
--- For links to this project, the uri is a relative path from  documentation root.
--- For links to other projects, the uri is a full url (including the domain)
--- @alias clinkT
--- | { uri: string, name: string, role: string, domain: string, priority: number, dispname: string, inv_name: string? }
--- Any other fields are irrelevant
---
--- Type for the global inventory
--- indexed by:
---   name
---   domain
--- @alias inventoryT
--- | table<string, table<string, clinkT[]>>

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
--- @type inventoryT
local inventory = {}
local CACHE_FILEPATH = qdoc_root .. "/.quarto/interlinks/inventory.bin"

--- Serialize an object
---
--- Limitations:
---   - Cannot handle self referencing tables
---   - Has a naive test for detecting arrays
---
--- @param obj table|string|number|string|nil object to serialize
--- @return string # The serialized object.
local function serialize(obj)
  -- Implemented with a list that accummulates tokens.
  -- Tried concatenating strings, it is very slow
  local acc = {}
  local depth = 0
  local _serialize

  local function table_tostring(tbl)
    depth = depth + 1
    acc[#acc+1] = "{"

    -- This is a naive test for an array. The only foolproof way
    -- is to iterate over the whole table
    local is_array = (#tbl > 0) or (next(tbl) == nil)
    local indent = string.rep(" ", depth)

    for k, v in pairs(tbl) do
      if not is_array then
        acc[#acc+1] = ("\n%s["):format(indent)
        _serialize(k)
        acc[#acc+1] = "] = "
      end
      _serialize(v)
      acc[#acc+1] = ", "
    end

    if is_array then
      acc[#acc] = nil
      indent = ""
    else
      indent = "\n" .. indent:sub(1, -2)
    end

    acc[#acc+1] =  indent .. "}"
    depth = depth - 1
  end

  local serialize_funcs = {
    ["nil"] = function(x) acc[#acc+1] = tostring(x) end,
    number = function(x) acc[#acc+1] = tostring(x) end,
    boolean = function(x) acc[#acc+1] = tostring(x) end,
    string = function(x) acc[#acc+1] = string.format("%q", x) end,
    table = table_tostring
  }

  -- Do the serializing
  function _serialize(x)
    local f = serialize_funcs[type(x)]
    assert(f, "Cannot serialize object of type: " .. type(x))
    f(x)
  end

  _serialize(obj)
  return table.concat(acc, "")
end

local function serialize_to_return_value2(obj)
  return "return " .. serialize(obj)
end

--- Check if file exists
---
--- @param filepath string
--- @return boolean
local function file_exists(filepath)
  local f = io.open(filepath, "r")
  if f then
    io.close(f)
    return true
  else
    return false
  end
end

--- Write to a file
--- Creates directories as required
---
--- @param content string
--- @param filepath string
--- @raise exception if file cannot be opened
local function write_to_file(content, filepath)
  local dir = filepath:gsub ("[^/]+$", "")
  pandoc.system.make_directory(dir, true)

  local file = io.open(filepath, "w")
  assert(file, "Could not open file: " .. filepath .. " for writing")
  file:write(content)
  file:close()
end

--- Read from a file
---
--- @param filepath string The file to read.
--- @return string # content of the file
--- @raise exception if file cannot be opened
local function read_from_file(filepath, read_params)
  if not read_params then
    read_params = "a"
  end

  local file = io.open(filepath, "r")
  assert(file, "Could not open file: " .. filepath .. " for reading")
  local content = file:read(read_params)
  file:close()
  return content
end


--- Cache to disk
---
--- @param obj any object to write to file
--- @param filepath string Where to write
local function cache_to_disk(obj, filepath)
  -- create a binary string representation of a function that
  -- returns the object being cached
  local obj_return = serialize_to_return_value2(obj)
  write_to_file(obj_return, filepath .. ".txt")
  local obj_func = load(obj_return)
  assert(obj_func, "Could not serialize object of type: " .. type(obj))
  local binary_fstr = string.dump(obj_func)
  write_to_file(binary_fstr, filepath)
end

--- Read cache obj
---
--- @param filepath string Where to read
--- @return any Cached object
local function read_disk_cache(filepath)
  return loadfile(filepath)()
end

--- Read inventory file
---
--- The format of the inventory file is
---
---     # Project: {project-name}
---     # Version: {project-version}
---     {name} {domain}:{role} {priority} {uri} {dispname}
---     {name} {domain}:{role} {priority} {uri} {dispname}
---     {name} {domain}:{role} {priority} {uri} {dispname}
---     ...
---
--- 1. The {dispname} matches until the end of the line, and
---    {dispname} == "-", it's value is the same as the {name}
--- 2. A {uri} that ends with "#$" has an anchor that is equal
---    to the {name}
---
--- This function cannot read a json inventory.
---
--- @param filepath string path to the inventory file.
local function read_inventory_text(filepath)
  local contents = read_from_file(filepath, "a")
  local project = contents:match("# Project: (%S+)")
  local version = contents:match("# Version: (%S+)")
  local data = {project = project, version = version, items = {}}

  local pattern =
    "^" ..
      "(.-)%s+" ..        -- name
      "([%S:]-):" ..      -- domain
      "([%S]+)%s+" ..     -- role
      "(%-?%d+)%s+" ..    -- priority
      "(%S*)%s+" ..       -- uri
      "(.-)\r?$"          -- dispname

  -- All non-empty lines that do not start with "#"
  -- should match the pattern
  for line in contents:gmatch("[^\r\n]+") do
    if not line:match("^#") then
      local name, domain, role, priority, uri, dispname = line:match(pattern)

      -- error out onl lines like
      -- " domain:role 1 uri dispname"
      if name == nil then
        error("Error parsing line: " .. line)
      end

      data.items[#data.items + 1] = {
        name = name,
        domain = domain,
        role = role,
        priority = tonumber(priority),
        uri = uri,
        dispname = dispname
      }
    end
  end
  return data
end

--- Add a source of links to the inventory
---
--- @param base_filepath string path to the file without an extension
---   This function tries .txt file then a .json
--- @param prefix string A prefix to the original uris in the inventory file
---   that makes them resolvable.
---   For external links, it should be the source url
---   For internal links, it should be a "/".
local function add_link_source_to_inventory(base_filepath, prefix)
  local txt_filepath = base_filepath .. ".txt"
  local json_filepath = base_filepath .. ".json"

  -- Try .txt then .json
  local status, project_inv = pcall(read_inventory_text, txt_filepath)
  if not status then
    local contents = read_from_file(json_filepath, "a")
    -- NOTE: Down the line, change to pandoc.json.decode as
    -- it now exposes the same method.
    project_inv = quarto.json.decode(contents)
    if not project_inv then
      return
    end
  end

  -- Insert new_item into table in assending priority
  local function priority_insert(tbl, new_item)
    local idx = #tbl
    for i, item in ipairs(tbl) do
      if new_item.priority > item.priority then
        idx = i
        break
      end
    end
    table.insert(tbl, idx, new_item)
  end

  -- Add the projects inventory items to the global inventory
  -- The key for each item is the prefixed-uri
  prefix = prefix or ""
  for _, item in ipairs(project_inv.items) do
    item.uri = prefix .. item.uri
    item.priority = tonumber(item.priority)
    if not inventory[item.name] then
      inventory[item.name] = {}
    end

    if inventory[item.name][item.domain] then
      priority_insert(inventory[item.name][item.domain], item)
    else
      inventory[item.name][item.domain] = {item}
    end
  end
end


--- Build inventory index from the sources
---
--- @param sources table<table<string>> A list of
--- (base filepaths, prefix) i.e. the inventory file and the
--- uri prefix that would make links resolvable.
local function build_inventory(sources)
  local base_filepath
  local prefix
  for _, item in pairs(sources) do
    base_filepath, prefix = item[1], item[2]
    add_link_source_to_inventory(base_filepath, prefix)
  end
end


--- Write inventory to file cache
---
local function write_inventory_cache()
  cache_to_disk(inventory, CACHE_FILEPATH)
end


--- Load inventory from the file cache
--- @return inventoryT
local function read_inventory_cache()
  local status, contents = pcall(read_disk_cache, CACHE_FILEPATH)
  if not status then
    return {}
  end
  return contents
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
  local domains = inventory[ilink.name] or {}

  --- Detect any attribute in the candidate item that defers from
  ---
  --- @param item clinkT
  local function attributes_can_match(item)
    return not (
      -- e.g. :external+<inv_name>:<domain>:<role>:`<name>`
      (item.inv_name and item.inv_name ~= ilink.inv_name) or
      (ilink.role and item.role ~= ilink.role) or
      (ilink.domain and item.domain ~= ilink.domain)
    )
  end

  --- Select potential references in from a list
  ---
  --- @param domain_tbl table<clinkT> links for a name reference all in
  --- the same domain and ordered in descending to priority.
  --- @return table<clinkT> # Matches with the highest priority
  local function select_from_domain(domain_tbl)
    local lst = {}
    for _, item in ipairs(domain_tbl) do
      if attributes_can_match(item) then
        if #lst > 0 then
          if lst[#lst].priority > item.priority then
            break
          end
        end
        table.insert(lst, item)
      end
    end
    return lst
  end

  --- Select potential references from multiple domains
  ---
  --- @param tbl table<string, table<clinkT>> Lists (per domain) of links for
  --- a name for each domain. These come from an entry in the inventory table.
  --- @return table<clinkT> # Matches with the highest priority
  local function select_across_domains(tbl)
    local lst = {}
    for _, candidates in pairs(tbl) do
      for _, item in ipairs(select_from_domain(candidates)) do
        -- NOTE: Currently getting away without checking
        -- the priority
        table.insert(lst, item)
      end
    end
    return lst
  end

  --- The domain & role of the interlink are optional and if they
  --- are missing, we prefer the py domain. This should match the
  --- user's intent nearly all the time.
  if not ilink.domain and not ilink.role then
    -- :target:
    if domains["py"] then
      results = select_from_domain(domains["py"])
    else
      results = select_across_domains(domains)
    end
  elseif not ilink.domain and ilink.role ~= nil then
    -- :role:target:
    results = select_across_domains(domains)
  elseif ilink.domain ~= nil and not ilink.role then
    -- :domain::target: # This should be rare
    results = select_from_domain(domains[ilink.domain])
  else
    -- :domain:role:target:
    results = select_across_domains(domains)
  end

  if #results == 1 then
    return results[1]
  elseif #results > 1 then
    print("Found multiple matches for " .. ilink.name)
    quarto.utils.dump(results)
  elseif #results == 0 then
    print("Found no matches for object: " .. ilink.name)
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
  elseif role == "mod" then
    return "module"
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
  return pandoc.Str(pandoc.utils.stringify(link.content))
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
  if not next(inventory) and file_exists(CACHE_FILEPATH) then
    inventory = read_inventory_cache()
    return
  end

  local base_filepath = qdoc_root .. "/objects"
  local prefix
  local sources = {
    { base_filepath, "/" },
  }

  for k, v in pairs(meta.interlinks.sources) do
    base_filepath = qdoc_root .. "/_inv/" .. k .. "_objects"
    prefix = pandoc.utils.stringify(v.url)
    table.insert(sources, {base_filepath, prefix})
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
