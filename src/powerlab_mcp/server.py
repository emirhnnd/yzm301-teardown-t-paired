"""MCP sunucusu: motoru çağıran ince adaptör. Hesap mantığı burada YOKTUR; powerlab.cli.compute çağrılır."""
from mcp.server.fastmcp import FastMCP
from powerlab.cli import compute

mcp = FastMCP("powerlab")


@mcp.tool()
def power_analysis_t_paired(mode: str, tails: int, dz: float, alpha: float,
                            power: float | None = None, n_total: int | None = None) -> dict:
    """Eşleştirilmiş (bağımlı) iki ortalama için t testi güç analizi.
    mode="a-priori": power verilir, gerekli çift sayısı N hesaplanır.
    mode="post-hoc": n_total (çift sayısı) verilir, güç hesaplanır.
    dz: etki büyüklüğü (fark ortalaması / fark standart sapması), tails: 1 ya da 2.
    Dönüş a-priori: ncp, critical_t, df, n_total, actual_power; post-hoc: ncp, critical_t, df, power; hata: {error, code, field}."""
    return compute(mode=mode, tails=tails, dz=dz, alpha=alpha, power=power, n_total=n_total)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
