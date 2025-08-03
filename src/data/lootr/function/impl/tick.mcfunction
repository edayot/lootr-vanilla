schedule function lootr:impl/tick 1t

execute 
    as @e[tag=lootr.barrel]
    at @s:
        execute unless block ~ ~ ~ minecraft:barrel run kill @s
        execute if block ~ ~ ~ minecraft:barrel[open=false]{lock:{}}:
            # save Items to databse
            execute 
                unless data block ~ ~ ~ components.minecraft:bundle_contents
                run data modify block ~ ~ ~ components.minecraft:bundle_contents set value []


            # Store
            function ~/store with block ~ ~ ~ components.minecraft:custom_data.lootr
            function ~/store:
                # if the entry already exist, delete
                $data remove block ~ ~ ~ components.minecraft:bundle_contents[{components:{"minecraft:custom_data":{player:$(last_player)}}}]

                # append a new to the list
                $data modify block ~ ~ ~ components.minecraft:bundle_contents append value { \
                    id:"minecraft:stone", \ 
                    count:1, \ 
                    components:{"minecraft:custom_data":{player:$(last_player)}} \
                }

                data modify storage lootr:main temp.Items set value []
                data modify storage lootr:main temp.Items set from block ~ ~ ~ Items
                execute 
                    in minecraft:overworld
                    as 93682a08-d099-4e8f-a4a6-1e33a3692301:
                        setblock -30000000 22 1610 air
                        setblock -30000000 22 1610 yellow_shulker_box
                        data modify block -30000000 22 1610 Items set from storage lootr:main temp.Items

                        item replace entity @s weapon.mainhand with air
                        loot replace entity @s weapon.mainhand mine -30000000 22 1610

                        data modify storage lootr:main temp.component set value []
                        data modify storage lootr:main temp.component set from entity @s equipment.mainhand.components."minecraft:container"


                data modify block ~ ~ ~ components.minecraft:bundle_contents[-1].components."minecraft:container" set from storage lootr:main temp.component
            

            data modify block ~ ~ ~ Items set value []




            setblock ~ ~1 ~ minecraft:iron_block
            data remove block ~ ~ ~ lock

