advancement revoke @s only lootr:impl/on_open

# Save player uuid
data modify storage lootr:main temp set value {}
data modify storage lootr:main temp.UUID set from entity @s UUID

function ~/on_hit:
    execute unless data block ~ ~ ~ components.minecraft:custom_data.lootr run return fail
    execute 
        align xyz 
        positioned ~.5 ~.5 ~.5
        unless entity @n[tag=lootr.barrel, distance=..0.5]
        run summon item_display ~ ~ ~ {Tags:["lootr.barrel"]}

    data modify block ~ ~ ~ lock set value {items:["minecraft:diamond"]}
    setblock ~ ~1 ~ gold_block

    function ~/set_current_player with storage lootr:main temp
    function ~/set_current_player:
        $data modify block ~ ~ ~ components.minecraft:custom_data.lootr.last_player set value "$(UUID)"

    function ~/choose with block ~ ~ ~ components.minecraft:custom_data.lootr
    function ~/choose:
        raw f'$execute if data block ~ ~ ~ components.minecraft:bundle_contents[{{components:{{"minecraft:custom_data":{{player:$(last_player)}}}}}}] run return run function {~/from_db} {{last_player:$(last_player)}}'

        function f"{~/from_db}":
            data modify storage lootr:main temp.component set value []
            $data modify storage lootr:main temp.component set from \
                block ~ ~ ~ components.minecraft:bundle_contents[{components:{"minecraft:custom_data":{player:$(last_player)}}}].components."minecraft:container"
            
            data modify block ~ ~ ~ Items set value []
            var = ~/loop
            execute 
                if data storage lootr:main temp.component[0] 
                run function f"{var}"
            function f"{var}":
                data remove storage lootr:main temp.item
                data modify storage lootr:main temp.item set from storage lootr:main temp.component[0].item
                data modify storage lootr:main temp.item.Slot set from storage lootr:main temp.component[0].slot

                data modify block ~ ~ ~ Items append from storage lootr:main temp.item

                data remove storage lootr:main temp.component[0]
                execute 
                    if data storage lootr:main temp.component[0] 
                    run function f"{var}"

                    

        data modify block ~ ~ ~ Items set value []
        $execute as @p[tag=lootr.player] run loot insert ~ ~ ~ loot $(loot_table)



tag @s add lootr.player 
execute anchored eyes positioned ^ ^ ^ run function #bs.raycast:run {with:{
    on_targeted_block: f"function {~/on_hit}",
}}
tag @s remove lootr.player 




