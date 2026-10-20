"""Chinese labels and concise usage hints for PalDefender RCON commands."""

from __future__ import annotations


COMMAND_HELP: dict[str, dict[str, str]] = {
    "adminlogin": {"title": "登录 PalDefender 管理员", "syntax": "adminlogin <管理员密码>", "detail": "在游戏聊天框登录 PalDefender 管理员模式。不要把真实密码保存到网页。"},
    "adminlogout": {"title": "退出管理员模式", "syntax": "adminlogout", "detail": "退出当前游戏角色的管理员模式。"},
    "getrconcmds": {"title": "获取全部 RCON 指令", "syntax": "getrconcmds", "detail": "读取服务器当前支持的 RCON 指令清单。"},
    "version": {"title": "查看游戏与插件版本", "syntax": "version", "detail": "返回 Palworld 与 PalDefender 版本。"},
    "reloadcfg": {"title": "重新加载配置", "syntax": "reloadcfg", "detail": "重新加载 Config、白名单和封禁数据。"},
    "addadminip": {"title": "添加管理员 IP", "syntax": "addadminip <IP>", "detail": "将 IP 地址加入管理员白名单。"},
    "setadmin": {"title": "授予或撤销临时管理员", "syntax": "setadmin <UserId>", "detail": "切换指定玩家的临时管理员身份。"},
    "pgbroadcast": {"title": "发送全服公告", "syntax": "pgbroadcast <消息>", "detail": "向服务器内所有玩家发送消息。"},
    "iwantplayerlist": {"title": "开启详细玩家列表", "syntax": "iwantplayerlist", "detail": "开启包含 UserId 与 PlayerUID 的玩家列表信息。"},
    "getpos": {"title": "查询玩家坐标", "syntax": "getpos [UserId]", "detail": "查询指定玩家所在位置。"},
    "settime": {"title": "设置游戏时间", "syntax": "settime <0-23|day|night>", "detail": "修改当前世界时间。"},
    "alert": {"title": "发送全服警报", "syntax": "alert <消息>", "detail": "向全服显示醒目的警报消息。"},
    "send": {"title": "向玩家发送消息", "syntax": "send <msg|log|ilog|vilog> <UserId> <消息>", "detail": "向指定玩家发送聊天或屏幕日志消息。"},
    "getnearestbase": {"title": "查询最近基地", "syntax": "getnearestbase <X> <Y> <Z>", "detail": "查询给定坐标附近基地的所属公会。"},
    "killnearestbase": {"title": "摧毁最近基地", "syntax": "killnearestbase <X> <Y> <Z>", "detail": "摧毁给定坐标最近的基地，无法撤销。"},
    "kick": {"title": "踢出玩家", "syntax": "kick <UserId> [原因]", "detail": "将玩家踢出当前服务器。"},
    "ban": {"title": "封禁玩家", "syntax": "ban <UserId> [原因]", "detail": "封禁并踢出指定玩家。"},
    "ipban": {"title": "封禁玩家 IP", "syntax": "ipban <UserId> [原因]", "detail": "封禁指定玩家当前使用的 IP。"},
    "banip": {"title": "封禁指定 IP", "syntax": "banip <IP>", "detail": "直接把 IP 地址加入封禁列表。"},
    "unban": {"title": "解除玩家封禁", "syntax": "unban <UserId> [原因]", "detail": "从 PalDefender 封禁列表移除玩家。"},
    "unbanip": {"title": "解除 IP 封禁", "syntax": "unbanip <IP>", "detail": "从封禁列表移除指定 IP。"},
    "getip": {"title": "查询玩家 IP", "syntax": "getip <UserId>", "detail": "返回指定玩家的连接 IP。"},
    "whitelist_add": {"title": "添加白名单玩家", "syntax": "whitelist_add <UserId>", "detail": "将玩家加入服务器白名单。"},
    "whitelist_remove": {"title": "移除白名单玩家", "syntax": "whitelist_remove <UserId>", "detail": "将玩家移出服务器白名单。"},
    "whitelist_get": {"title": "查看白名单", "syntax": "whitelist_get", "detail": "显示当前完整白名单。"},
    "tp": {"title": "传送玩家", "syntax": "tp <UserId> <目标UserId|X Y [Z]|home|oilrig>", "detail": "把指定玩家传送到玩家、坐标、基地或油田。"},
    "give_exp": {"title": "发放角色经验", "syntax": "give_exp <UserId> <数量>", "detail": "增加指定玩家的角色经验值。"},
    "giveme_exp": {"title": "给自己经验", "syntax": "giveme_exp <数量>", "detail": "给命令执行者增加角色经验；RCON 没有游戏角色时可能不可用。"},
    "renameplayer": {"title": "修改玩家昵称", "syntax": "renameplayer <UserId> <新昵称>", "detail": "修改指定玩家的显示名称。"},
    "givestats": {"title": "增减属性点", "syntax": "givestats <UserId> [数量=1]", "detail": "增加未使用属性点，负数表示扣除。"},
    "setguildleader": {"title": "设置公会会长", "syntax": "setguildleader <UserId>", "detail": "将指定玩家设为其当前公会会长。"},
    "exportguilds": {"title": "导出全部公会", "syntax": "exportguilds", "detail": "把服务器公会数据导出到 PalDefender 文件夹。"},
    "give": {"title": "发放单种物品", "syntax": "give <UserId> <ItemId> [数量=1]", "detail": "向玩家发放一种物品。"},
    "giveitems": {"title": "批量发放物品", "syntax": "giveitems <UserId> <ItemId:数量> ...", "detail": "一次向玩家发放多种物品。"},
    "give_relic": {"title": "发放遗物强化点", "syntax": "give_relic <UserId> <RelicType> [数量=1]", "detail": "增加指定类型的遗物强化点。"},
    "delitem": {"title": "删除单种物品", "syntax": "delitem <UserId> <ItemId> [数量=1|all]", "detail": "从玩家背包删除一种物品。"},
    "delitems": {"title": "批量删除物品", "syntax": "delitems <UserId> <ItemId:数量> ...", "detail": "从玩家背包一次删除多种物品。"},
    "clearinv": {"title": "清空玩家背包", "syntax": "clearinv <UserId> [items|keyitems|armor|weapons|food|dropslot|all]", "detail": "清空指定背包容器，无法由面板恢复。"},
    "givepal": {"title": "发放帕鲁", "syntax": "givepal <UserId> <PalId> [等级=1]", "detail": "向玩家发放指定种类和等级的帕鲁。"},
    "givepal_j": {"title": "按模板发放帕鲁", "syntax": "givepal_j <UserId> <PalTemplate文件名>", "detail": "使用 PalTemplate 文件向玩家发放帕鲁。"},
    "giveegg": {"title": "发放帕鲁蛋", "syntax": "giveegg <UserId> <EggId> <PalId> [等级]", "detail": "发放包含指定帕鲁的帕鲁蛋。"},
    "givemeegg": {"title": "给自己帕鲁蛋", "syntax": "givemeegg <EggId> <PalId> [等级]", "detail": "给命令执行者发放帕鲁蛋。"},
    "giveegg_j": {"title": "按模板发放帕鲁蛋", "syntax": "giveegg_j <EggId> <PalTemplate文件名> [等级]", "detail": "使用 PalTemplate 文件生成帕鲁蛋。"},
    "givemeegg_j": {"title": "按模板给自己帕鲁蛋", "syntax": "givemeegg_j <EggId> <PalTemplate文件名> [等级]", "detail": "使用 PalTemplate 文件给执行者生成帕鲁蛋。"},
    "exportpals": {"title": "导出玩家全部帕鲁", "syntax": "exportpals [UserId]", "detail": "把玩家帕鲁导出为 PalTemplate 文件。"},
    "deletepals": {"title": "按条件删除帕鲁", "syntax": "deletepals <UserId> <过滤条件>", "detail": "按 ID、等级、性别、词条等条件删除帕鲁，风险极高。"},
    "learntech": {"title": "学习科技", "syntax": "learntech <UserId> <TechId|all>", "detail": "让玩家学习指定科技或全部科技。"},
    "unlearntech": {"title": "遗忘科技", "syntax": "unlearntech <UserId> <TechId|all>", "detail": "让玩家遗忘指定科技或全部科技。"},
    "givetechpoints": {"title": "发放科技点", "syntax": "givetechpoints <UserId> [数量=1]", "detail": "增加普通科技点。"},
    "givebosstechpoints": {"title": "发放古代科技点", "syntax": "givebosstechpoints <UserId> [数量=1]", "detail": "增加古代科技点。"},
    "getskinids": {"title": "查看皮肤 ID", "syntax": "getskinids", "detail": "列出当前支持的皮肤内部 ID。"},
    "gettechids": {"title": "查看科技 ID", "syntax": "gettechids", "detail": "列出当前支持的科技内部 ID。"},
    "spawnpal": {"title": "在世界生成帕鲁", "syntax": "spawnpal <PalId> <X> <Y> <Z> [等级]", "detail": "在指定坐标生成帕鲁；RCON 必须提供坐标。"},
    "spawnpal_j": {"title": "按模板生成帕鲁", "syntax": "spawnpal_j <PalTemplate文件名> <X> <Y> <Z>", "detail": "使用 PalTemplate 文件在指定坐标生成帕鲁。"},
    "summon": {"title": "执行帕鲁召唤文件", "syntax": "summon <PalSummon文件名>", "detail": "运行 PalDefender 的 PalSummon 配置文件。"},
    "togglepvp": {"title": "切换 PvP", "syntax": "togglepvp", "detail": "切换本次服务器运行期间的 PvP 状态。"},
    "gotonearestbase": {"title": "前往最近基地", "syntax": "gotonearestbase [X] [Y] [Z]", "detail": "把自己传送到当前位置或指定坐标附近的基地。"},
    "imcheater": {"title": "测试反作弊响应", "syntax": "imcheater", "detail": "模拟作弊者行为以测试服务器响应。"},
    "spectate": {"title": "开启观察者模式", "syntax": "spectate", "detail": "让当前游戏角色进入观察者模式。"},
    "givemestats": {"title": "给自己属性点", "syntax": "givemestats [数量=1]", "detail": "增加自己的未使用属性点，负数表示扣除。"},
    "godmode": {"title": "切换无敌模式", "syntax": "godmode [on|off]", "detail": "开启、关闭或切换当前角色的无敌模式。"},
    "giveme": {"title": "给自己物品", "syntax": "giveme <ItemId> [数量=1]", "detail": "向当前游戏角色发放一种物品。"},
    "giveme_relic": {"title": "给自己遗物强化点", "syntax": "giveme_relic <RelicType> [数量=1]", "detail": "增加当前角色指定类型的遗物强化点。"},
    "givemepal": {"title": "给自己帕鲁", "syntax": "givemepal <PalId> [等级=1]", "detail": "向当前游戏角色发放指定帕鲁。"},
    "givemepal_j": {"title": "按模板给自己帕鲁", "syntax": "givemepal_j <PalTemplate文件名>", "detail": "使用 PalTemplate 文件给当前角色发放帕鲁。"},
    "jetragon": {"title": "领取管理员空涡龙", "syntax": "jetragon", "detail": "给当前管理员一只特殊的 Admin Jetragon。"},
    "catwaifu": {"title": "领取管理员猫娘", "syntax": "catwaifu", "detail": "给当前管理员一只可强化角色属性的特殊帕鲁。"},
    "givemetechpoints": {"title": "给自己科技点", "syntax": "givemetechpoints [数量=1]", "detail": "增加当前角色的普通科技点。"},
    "givemebosstechpoints": {"title": "给自己古代科技点", "syntax": "givemebosstechpoints [数量=1]", "detail": "增加当前角色的古代科技点。"},
}


def ingame_commands() -> list[dict[str, str]]:
    """Return commands available in PalDefender's in-game admin chat mode."""
    chat_syntax = {
        "getnearestbase": "getnearestbase [X] [Y] [Z]",
        "spawnpal": "spawnpal <PalId> [等级] [X Y Z]",
        "spawnpal_j": "spawnpal_j <PalTemplate文件名> [X Y Z]",
        "tp": "tp <玩家|坐标|home|oilrig>",
    }
    commands = []
    for name, help_item in COMMAND_HELP.items():
        if name == "getrconcmds":
            continue
        item = {"name": name, **help_item}
        item["syntax"] = chat_syntax.get(name, item["syntax"])
        commands.append(item)
    return sorted(commands, key=lambda item: item["name"])


def get_command_help(name: str) -> dict[str, str]:
    return COMMAND_HELP.get(
        name,
        {"title": "服务器扩展指令", "syntax": name, "detail": "该指令由当前服务器动态公布，暂无本地中文说明。"},
    )
