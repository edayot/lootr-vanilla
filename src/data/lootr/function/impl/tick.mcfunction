schedule function lootr:impl/tick 1t

execute 
    as @e[tag=lootr.barrel]
    at @s:
        execute unless block ~ ~ ~ minecraft:barrel run kill @s
        execute if block ~ ~ ~ minecraft:barrel[open=false]{lock:{}}:
            # save Items to databse
            execute 
                unless data block ~ ~ ~ components.minecraft:custom_data.lootr.database 
                run data modify block ~ ~ ~ components.minecraft:custom_data.lootr.database set value {}


            function ~/set_database with block ~ ~ ~ components.minecraft:custom_data.lootr
            function ~/set_database:
                $data modify block ~ ~ ~ components.minecraft:custom_data.lootr.database."$(last_player)" set from block ~ ~ ~ Items
            

            data modify block ~ ~ ~ Items set value []




            setblock ~ ~1 ~ minecraft:iron_block
            data remove block ~ ~ ~ lock

